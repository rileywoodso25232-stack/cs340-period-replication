/*
 * period_l1.c —— Period (ICSE'22) 的 L1 最小复现
 *
 * 目标：在普通 macOS/Linux 用户态，用 pthread + 条件变量模拟论文的“周期调度
 *      (periodical execution)”，并在 CVE-2016-1972 的简化程序上复现论文图 3
 *      中的三个 bug：NPD（空指针解引用）、UAF（释放后使用）、DF（二次释放）。
 *
 * 核心思想：
 *   - 一个 schedule 是若干“周期”的序列，每个周期 = {线程号, 配额}；
 *   - 线程每走到一个“关键点”，先过检查站 sched_point()：
 *       轮到我 且 本周期配额没用完  -> 放行（配额 -1）
 *       本周期配额用完             -> 进入下一个周期
 *       不是我的周期               -> 阻塞，等下一个周期
 *   - 所有周期走完后，剩下的关键点不再受控（自由跑）。
 *
 * 这不是论文的完整实现（没有 SCHED_DEADLINE、没有自动调度生成器、bug 判定是
 * 手写的“预言器”），但它足以把“周期=切换”这件事跑给你看。
 *
 * 编译： cc -O0 -g -pthread period_l1.c -o period_l1
 * 运行： ./period_l1
 */

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NT 2            /* 两个线程 T0, T1 */
#define MAXP 32         /* 最多支持 32 个周期 */

#ifndef USE_ORACLE
#define USE_ORACLE 1    /* 1 = 用显式检查判定 bug；0 = 让 ASan/系统去抓真错误 */
#endif

typedef struct {
    int tid;            /* 这个周期归哪个线程 */
    int quota;          /* 这个周期允许它执行几个关键点 */
} period_t;

/* ---------------- 调度器状态 ---------------- */
static period_t        g_sched[MAXP];
static int             g_np;        /* 周期个数 */
static int             g_cur;       /* 当前周期下标 */
static int             g_used;      /* 当前周期已消耗的配额 */

static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  g_cv = PTHREAD_COND_INITIALIZER;

static int  g_ready;                /* 已就绪线程数（启动栅栏） */
static int  g_start;                /* 是否放行 */
static int  g_stop;                 /* 已触发 bug，提前结束本次调度 */
static int  g_bug;
static int  g_dead[NT];             /* 线程是否已退出 */
static int  g_kp[NT];               /* 线程已执行的关键点个数 */
static char g_msg[256];

/* ---------------- 被测程序状态 ---------------- */
static int              done;       /* 对应论文的 static int done = 0; */
static long             waiters;    /* 对应论文的 static long waiters = 0; */
static int              freed;      /* lock 是否已被 free（但可能还没置 NULL） */
static int              locked;     /* lock 当前是否处于加锁状态 */
static pthread_mutex_t *lockp;      /* 对应论文的 static pthread_mutex_t* lock; */

/* ---------------- bug 报告（预言器） ---------------- */
static void report_bug(int tid, const char *kind, const char *kp, const char *why)
{
    pthread_mutex_lock(&g_mu);
    if (!g_bug) {
        g_bug = 1;
        snprintf(g_msg, sizeof g_msg, "%s：T%d 在 %s 处%s", kind, tid, kp, why);
    }
    g_stop = 1;
    pthread_cond_broadcast(&g_cv);
    pthread_mutex_unlock(&g_mu);
}

/* ---------------- 调度检查站 ---------------- */
/*
 * 返回值：1 = 可以继续执行；0 = 本次调度因 bug 终止，调用者应立即返回。
 * 调用前 g_kp[tid] 指向“即将执行的关键点下标”。
 */
static int sched_point(int tid, const char *name)
{
    pthread_mutex_lock(&g_mu);
    for (;;) {
        if (g_stop) {
            pthread_mutex_unlock(&g_mu);
            return 0;
        }
        if (g_cur >= g_np) {            /* 周期用完了：尾部自由执行 */
            pthread_mutex_unlock(&g_mu);
            return 1;
        }
        period_t *p = &g_sched[g_cur];
        if (p->quota <= 0 || g_used >= p->quota) {   /* 本周期配额用完 -> 换周期 */
            g_cur++;
            g_used = 0;
            pthread_cond_broadcast(&g_cv);
            continue;
        }
        if (p->tid == tid) {            /* 轮到我：消耗一个配额，放行 */
            printf("    [P%d] T%d  %-4s  (done=%d, waiters=%ld, %s)\n",
                   g_cur + 1, tid, name, done, waiters,
                   lockp == NULL ? "lock=NULL" : (freed ? "lock=已释放" : (locked ? "lock=使用中" : "lock=可用")));
            fflush(stdout);
            g_used++;
            pthread_mutex_unlock(&g_mu);
            return 1;
        }
        pthread_cond_wait(&g_cv, &g_mu); /* 不是我的周期：等 */
    }
}

/* 关键点入口宏：过检查站 + 计数 */
#define KP(tid, name) do {                             \
        if (!sched_point((tid), (name))) return;       \
        g_kp[(tid)]++;                                 \
    } while (0)

/* ---------------- 被插桩的“关键操作” ---------------- */
static void lock_acquire(int tid, const char *kp)
{
#if USE_ORACLE
    if (!lockp) {
        report_bug(tid, "NPD（空指针解引用）", kp, "对 lock == NULL 调用 pthread_mutex_lock");
        return;
    }
    if (freed) {
        report_bug(tid, "UAF（释放后使用）", kp, "对已经 free 过的 lock 调用 pthread_mutex_lock");
        return;
    }
#else
    /* 真正读一下 lock 指向的内存：模拟 pthread_mutex_lock 内部对锁对象的访问，
       让 AddressSanitizer 能报出 heap-use-after-free（系统库自身没有被插桩）。 */
    if (lockp != NULL) {
        volatile unsigned char probe = *(volatile unsigned char *)lockp;
        (void)probe;
    }
#endif
    pthread_mutex_lock(lockp);
    locked = 1;
}

static void lock_release(int tid, const char *kp)
{
#if USE_ORACLE
    if (!lockp) {
        report_bug(tid, "NPD（空指针解引用）", kp, "对 lock == NULL 调用 pthread_mutex_unlock");
        return;
    }
    if (freed) {
        report_bug(tid, "UAF（释放后使用）", kp, "对已经 free 过的 lock 调用 pthread_mutex_unlock");
        return;
    }
#endif
    pthread_mutex_unlock(lockp);
    locked = 0;
}

static void lock_free(int tid, const char *kp)
{
#if USE_ORACLE
    if (freed) {
        report_bug(tid, "DF（二次释放）", kp, "对已经 free 过的 lock 再次调用 free");
        return;
    }
#endif
    freed = 1;
    pthread_mutex_destroy(lockp);
    free(lockp);
}

/* ---------------- 被测函数 once() ---------------- */
static void once_body(int tid)
{
    KP(tid, "L6");
    if (done) return;                 /* L6-7：已经有人做过，直接返回 */

    KP(tid, "L8");  ++waiters;        /* L8  */
    KP(tid, "L9");  lock_acquire(tid, "L9");   /* L9 */

    KP(tid, "L11");                   /* L11 if (!done) */
    if (!done) {
        KP(tid, "L12"); done = 1;     /* L12 */
    }

    KP(tid, "L13"); lock_release(tid, "L13");    /* L13 */

    KP(tid, "L14");                   /* L14 if (--waiters == 0) */
    if (--waiters == 0) {
        KP(tid, "L15"); lock_free(tid, "L15");  /* L15 */
        KP(tid, "L16"); lockp = NULL;          /* L16 */
    }
}

/* ---------------- 线程收尾：把“已死线程”占着的周期跳过 ---------------- */
static void thread_done(int tid)
{
    pthread_mutex_lock(&g_mu);
    g_dead[tid] = 1;
    while (g_cur < g_np && g_dead[g_sched[g_cur].tid]) {
        g_cur++;
        g_used = 0;
    }
    pthread_cond_broadcast(&g_cv);
    pthread_mutex_unlock(&g_mu);
}

static void *worker(void *arg)
{
    int tid = (int)(long)arg;

    pthread_mutex_lock(&g_mu);
    g_ready++;
    pthread_cond_broadcast(&g_cv);
    while (!g_start)
        pthread_cond_wait(&g_cv, &g_mu);
    pthread_mutex_unlock(&g_mu);

    once_body(tid);
    thread_done(tid);
    return NULL;
}

/* ---------------- 单次“实验” ---------------- */
static void print_schedule(void)
{
    for (int i = 0; i < g_np; i++)
        printf("%s{T%d×%d}", i ? "·" : "", g_sched[i].tid, g_sched[i].quota);
}

static void reset_state(void)
{
    g_cur = 0;
    g_used = 0;
    g_stop = 0;
    g_bug = 0;
    g_ready = 0;
    g_start = 0;
    g_msg[0] = '\0';
    for (int i = 0; i < NT; i++) {
        g_dead[i] = 0;
        g_kp[i] = 0;
    }
    done = 0;
    waiters = 0;
    freed = 0;
    locked = 0;
    lockp = malloc(sizeof(pthread_mutex_t));
    if (!lockp) {
        perror("malloc");
        exit(1);
    }
    pthread_mutex_init(lockp, NULL);
}

static int run_case(const char *name, const period_t *sch, int n)
{
    memcpy(g_sched, sch, (size_t)n * sizeof *sch);
    g_np = n;
    reset_state();

    printf("\n=== %s\n", name);
    printf("    调度: ");
    print_schedule();
    printf("\n");

    pthread_t th[NT];
    for (long i = 0; i < NT; i++) {
        if (pthread_create(&th[i], NULL, worker, (void *)i) != 0) {
            perror("pthread_create");
            exit(1);
        }
    }

    pthread_mutex_lock(&g_mu);
    while (g_ready < NT)
        pthread_cond_wait(&g_cv, &g_mu);
    g_start = 1;
    pthread_cond_broadcast(&g_cv);
    pthread_mutex_unlock(&g_mu);

    for (int i = 0; i < NT; i++)
        pthread_join(th[i], NULL);

    if (g_bug)
        printf("    >>> 触发 bug：%s\n", g_msg);
    else
        printf("    >>> 未触发 bug（这个调度是安全的）\n");
    return g_bug;
}

/* ---------------- 待测的 5 个调度 ---------------- */

/* 论文图 3(g)：3 个周期触发 NPD，最后补一个周期让 T1 跑尾部 */
static const period_t S_NPD[] = {
    {0, 1}, {1, 1}, {0, 8}, {1, 8}
};

/* 论文图 3(i)：5 个周期触发 UAF */
static const period_t S_UAF[] = {
    {0, 4}, {1, 1}, {0, 4}, {1, 7}, {0, 1}, {1, 1}
};

/* 论文图 3(j)：6 个周期触发 DF */
static const period_t S_DF[] = {
    {0, 4}, {1, 1}, {0, 3}, {1, 6}, {0, 2}, {1, 1}
};

/* 对照：T0 一口气做完，T1 在 L6 看到 done==1 直接返回，没有 bug */
static const period_t S_SAFE[] = {
    {0, 9}, {1, 9}
};

/* 变体：先让 T1 过 L6，再让 T0 跑一大段，同样能撞出 UAF */
static const period_t S_VAR[] = {
    {1, 1}, {0, 8}, {1, 9}
};

typedef struct {
    const char   *key;     /* 命令行用的短名 */
    const char   *name;    /* 打印用的名字 */
    const period_t *sch;
    int            n;
} case_t;

static const case_t CASES[] = {
    { "npd",  "NPD（论文图 3(g) 的配方，末尾补 T1 的尾部）", S_NPD,  4 },
    { "uaf",  "UAF（论文图 3(i) 的配方）",                    S_UAF,  6 },
    { "df",   "DF （论文图 3(j) 的配方）",                    S_DF,   6 },
    { "safe", "对照：T0 先完整跑完",                          S_SAFE, 2 },
    { "var",  "变体：T1 先过 L6",                             S_VAR,  3 },
};

int main(int argc, char **argv)
{
    setvbuf(stdout, NULL, _IONBF, 0);

    printf("Period L1 最小复现 —— CVE-2016-1972 简化版\n");
    printf("两个线程 T0/T1，各 9 个关键点：L6 L8 L9 L11 L12 L13 L14 L15 L16\n");

    const char *only = (argc > 1) ? argv[1] : "all";
    int total = 0, bugs = 0;

    for (size_t i = 0; i < sizeof CASES / sizeof CASES[0]; i++) {
        if (strcmp(only, "all") != 0 && strcmp(only, CASES[i].key) != 0)
            continue;
        total++;
        bugs += run_case(CASES[i].name, CASES[i].sch, CASES[i].n);
    }

    if (total == 0) {
        fprintf(stderr, "未知用例：%s（可选：npd uaf df safe var all）\n", only);
        return 2;
    }
    printf("\n==== 汇总：%d 个调度中有 %d 个触发了 bug ====\n", total, bugs);
    return 0;
}

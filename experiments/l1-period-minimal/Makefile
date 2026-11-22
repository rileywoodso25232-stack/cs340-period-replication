CC      ?= cc
CFLAGS  ?= -O0 -g -Wall -Wextra -pthread

all: period_l1

period_l1: period_l1.c
	$(CC) $(CFLAGS) period_l1.c -o $@

run: period_l1
	./period_l1

# 关掉“预言器”，让真实的系统/ASan 去抓错误（用来证明 bug 不是编出来的）
period_l1_asan: period_l1.c
	$(CC) -O0 -g -fsanitize=address -DUSE_ORACLE=0 -pthread period_l1.c -o $@

demo-asan: period_l1_asan
	-./period_l1_asan npd
	-./period_l1_asan uaf
	-./period_l1_asan df

clean:
	rm -f period_l1 period_l1_asan

\# PERIOD 鐜鎼缓涓庡畨瑁呴獙璇佹潗鏂?



\## 鎻愪氦浜?

\- 瀛﹀彿锛?240014957

\- 鍏ㄥ悕锛氬惔鏄庨槼



\## 瀹屾垚鎯呭喌

宸插畬鎴?PERIOD 鐜閰嶇疆锛屽苟鎴愬姛閲嶆斁 doubleFree 绀轰緥鐨勪竴涓け璐ヨ皟搴︺€?

AddressSanitizer 鎶ュ憡 double-free锛岃鏄庤璋冨害鍙互鍐嶆瑙﹀彂閲嶅閲婃斁閿欒銆?

鏈鏉愭枡鐢ㄤ簬鐜涓庡畨瑁呴獙璇侊紝涓嶄唬琛ㄨ鏂囦富瀹為獙宸插畬鎴愩€?



\## 瀹為檯鐜

\- 杩愯鏂瑰紡锛欴ocker锛屼娇鐢?WSL2 Linux 鍐呮牳

\- 瀹瑰櫒绯荤粺锛歎buntu 18.04.6 LTS

\- 鍐呮牳锛?.18.33.2-microsoft-standard-WSL2

\- GCC锛?.5.0

\- Clang锛?0.0.0

\- Python 3锛?.6.9

\- PERIOD 鎻愪氦锛歝b8deb9a176e5bb292d70d46557dd61dc0e98069

\- Docker 闀滃儚鍚嶇О锛歱eriod:cb8deb9

\- 鏈湴闀滃儚 ID锛歴ha256:5ab9c6dec0438d00f35f21a02c127aeed628236c470cabf2fcbec453379f57a2

\- 瀹瑰櫒鍚嶇О锛歱eriod-cs340

\- 鐗规潈妯″紡锛氬紑鍚?

\- 鎸傝浇鐩綍锛氭棤

\- 瀹瑰櫒鍐呬唬鐮佺洰褰曪細/workdir/PERIOD



\## 鏉愭枡璇存槑

浠ヤ笅閾炬帴浠ユ湰璇存槑鏂囦欢鎵€鍦ㄧ洰褰曚负鍩哄噯锛?



\- \[environment.txt](environment.txt)锛氱郴缁熴€佸唴鏍搞€佷唬鐮佹彁浜ゅ拰缂栬瘧鍣ㄧ増鏈褰曘€?

\- \[Dockerfile.repro](Dockerfile.repro)锛氫粠瀹瑰櫒浠ｇ爜鐩綍涓繚瀛樼殑鎼缓鏂囦欢锛涘皻鏈‘璁ゅ綋鍓嶉暅鍍忔槸鍚︾敱姝ゆ枃浠舵瀯寤恒€?

\- \[閲嶆斁鏃ュ織](../../results/raw/setup-smoke/replay.log)锛氭湰娆″け璐ヨ皟搴﹂噸鏀剧殑杈撳嚭鏃ュ織銆?

\- \[澶辫触璋冨害鐩綍](../../results/raw/setup-smoke/out_df_1/Errors/)锛氭鍓嶈繍琛屼繚瀛樼殑 4 涓け璐ヨ皟搴︽枃浠躲€傝繖浜涙枃浠朵笉浠ｈ〃 4 绉嶄笉鍚岀己闄枫€?

\- 瀹瑰櫒閰嶇疆鍘熷璁板綍 container-inspect.json 淇濈暀鍦ㄦ湰鍦板浠戒腑锛屾湰娆℃湭鎻愪氦銆?



\## 宸查獙璇佺殑閲嶆斁鏂规硶



浠ヤ笅姝ラ閫傜敤浜庢湰鏈哄凡鏈夊鍣紝灏氫笉鏄叏鏂版満鍣ㄤ笂鐨勫畬鏁村畨瑁呮祦绋嬨€?



鍦?Windows PowerShell 涓惎鍔ㄥ苟杩涘叆宸叉湁瀹瑰櫒锛?



```powershell

docker start -ai period-cs340

```



濡傛灉瀹瑰櫒宸插湪杩愯锛屽彲鏀圭敤锛?



```powershell

docker exec -it period-cs340 /bin/bash

```



杩涘叆瀹瑰櫒鍚庝緷娆℃墽琛岋細



```bash

cd /workdir/PERIOD

source tool/init_env.sh

cd test/doubleFree

"$ROOT_DIR/tool/DBDS/run_PDS.py" -r out_df_1/Errors/000001_0000003_double-free ./df

```



瀹為檯杈撳嚭鍖呭惈锛?



```text

ERROR: AddressSanitizer: attempting double-free

SUMMARY: AddressSanitizer: double-free

ABORTING

```



缁撹锛氫繚瀛樼殑澶辫触璋冨害鎴愬姛鍐嶆瑙﹀彂 double-free 閿欒銆?

ABORTING 琛ㄧず娴嬭瘯绋嬪簭妫€娴嬪埌閿欒鍚庣粓姝€?



\## 褰撳墠闄愬埗涓庡悗缁伐浣?

\- 灏氭湭瀹屾垚渚濇嵁杩欎唤鏉愭枡鍦ㄥ叏鏂版満鍣ㄤ笂鐨勬瀯寤洪獙璇併€?

\- 灏氭湭纭褰撳墠闀滃儚鏄惁鐢卞浠界殑 Dockerfile.repro 鏋勫缓銆?

\- 鍘熷娴嬭瘯鐨勫畬鏁存帶鍒跺彴鏃ュ織灏氭湭鏀堕泦锛況eplay.log 鏄湰娆￠噸鏂版墽琛岄噸鏀炬椂淇濆瓨鐨勬棩蹇椼€?

\- 涓嶈兘浠呭嚟 4 涓け璐ヨ皟搴︽枃浠舵帹鏂€昏皟搴︽暟銆佷笉鍚岀己闄锋暟閲忔垨杩愯鑰楁椂銆?

\- 鍚庣画闇€瑕佽ˉ鍏呮寮忓疄楠岄厤缃€佽嚦灏戜笁娆＄嫭绔嬭繍琛岀殑鏁版嵁銆佽鏂囩粨鏋滃姣斻€佸樊寮傚垎鏋愬強鎵╁睍瀹為獙銆?



\## AI 浣跨敤璇存槑

浣跨敤 ChatGPT 杈呭姪鏁寸悊鎿嶄綔鍛戒护銆佽В閲婄粓绔緭鍑哄拰缂栧啓鏉愭枡璇存槑銆?

鐜閰嶇疆鍙婃祴璇曟墽琛岀敱鏈汉瀹為檯鎿嶄綔锛岃繍琛岀粨鏋滃凡鏍稿銆?



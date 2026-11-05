@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "BACKEND=http://127.0.0.1:3000"
set "PORT=8001"
set "BASE=http://127.0.0.1:%PORT%"
set "MSG=测试连接，请简短回复"
set "PASS=0"
set "FAIL=0"

echo.
echo ==============================================
echo  云游 Wander 数据链路诊断 (test.bat)
echo  逐段验证: 后端 -^> 直连 SSE -^> serve.py 代理 -^> 前端同款解析
echo  全程约 1-4 分钟（会调用两次模型）
echo ==============================================
echo.

rem ---------- 1. 工具与环境 ----------
where curl >nul 2>nul
if errorlevel 1 (echo  [FAIL] 未找到 curl（Windows 10 1803+ 自带）& set /a FAIL+=1) else (echo  [PASS] curl 可用& set /a PASS+=1)

python -c "print(1)" >nul 2>nul
if errorlevel 1 (echo  [FAIL] 未找到 python& set /a FAIL+=1) else (echo  [PASS] python 可用& set /a PASS+=1)

findstr /c:"ProxyHandler" serve.py >nul 2>nul
if errorlevel 1 (echo  [警告] 本目录 serve.py 是旧版，缺少代理直连修复！请更新。) else (echo  [PASS] serve.py 已含代理直连修复)

rem ---------- 2. 端口 3000 占用情况 ----------
echo  --- 端口 3000 占用情况（没有输出 = 后端没在运行）---
netstat -ano | findstr /c:"LISTENING" | findstr /c:":3000 "
echo  ---

rem ---------- 3. 后端健康检查（没运行会自动拉起） ----------
curl -s --noproxy "*" -m 3 "%BACKEND%/" > health.tmp 2>nul
findstr /c:"\"status\":\"Ok\"" health.tmp >nul 2>nul
if not errorlevel 1 goto backend_up

echo  [FAIL] 后端未运行，正在自动启动（弹出「云游-后端」窗口）...
start "云游-后端 (test.bat 拉起)" cmd /k "python main.py"
set /a TRY=0
:poll_backend
timeout /t 2 /nobreak >nul
curl -s --noproxy "*" -m 3 "%BACKEND%/" > health.tmp 2>nul
findstr /c:"\"status\":\"Ok\"" health.tmp >nul 2>nul
if not errorlevel 1 goto backend_auto_ok
set /a TRY+=1
if !TRY! lss 20 goto poll_backend
echo  [FAIL] 后端 40 秒内没有起来。请看「云游-后端」窗口里的报错并截图。
set /a FAIL+=1
goto backend_done

:backend_up
echo  [PASS] 后端已在运行 %BACKEND%
set /a PASS+=1
goto backend_done

:backend_auto_ok
echo  [PASS] 后端已自动拉起 %BACKEND%
set /a PASS+=1

:backend_done

rem ---------- 4. 直连后端 /web ----------
echo  正在直连后端获取 SSE（最长 120 秒）...
curl -s --noproxy "*" -m 120 -N --get "%BACKEND%/web" --data-urlencode "content=%MSG%" > direct.txt 2>nul
for %%A in (direct.txt) do set "DSIZE=%%~zA"
if !DSIZE! gtr 0 (echo  [PASS] 直连收到 !DSIZE! 字节& set /a PASS+=1) else (echo  [FAIL] 直连无任何输出（后端没吐数据）& set /a FAIL+=1)
echo  --- 原始内容前 400 字节 ---
powershell -NoProfile -Command "$b=[IO.File]::ReadAllBytes('direct.txt'); $n=[Math]::Min(400,$b.Length); [Console]::OutputEncoding=[Text.Encoding]::UTF8; [Text.Encoding]::UTF8.GetString($b,0,$n)"
echo  ---

rem ---------- 5. 经 serve.py 代理 ----------
echo  正在启动测试用 serve.py（端口 %PORT%）...
start /b "" cmd /c "set AGENT_BACKEND=%BACKEND%&& set FRONTEND_PORT=%PORT%&& python -u serve.py > serve_test.log 2>&1"
timeout /t 2 /nobreak >nul

curl -s --noproxy "*" -m 5 -o nul -w "%%{http_code}" "%BASE%/" > page_code.tmp 2>nul
set /p PCODE=<page_code.tmp
if "!PCODE!"=="200" (echo  [PASS] 静态页面 HTTP 200& set /a PASS+=1) else (echo  [FAIL] 静态页面 HTTP !PCODE!& set /a FAIL+=1)

echo  正在经 serve.py 获取 SSE（最长 120 秒）...
curl -s --noproxy "*" -m 120 -N -o proxied.txt -w "%%{http_code}" --get "%BASE%/web" --data-urlencode "content=%MSG%" > proxy_code.tmp 2>nul
set /p PXYCODE=<proxy_code.tmp
for %%A in (proxied.txt) do set "PSIZE=%%~zA"
if "!PXYCODE!"=="200" (
    if !PSIZE! gtr 0 (echo  [PASS] 代理收到 !PSIZE! 字节& set /a PASS+=1) else (echo  [FAIL] 代理 HTTP 200 但 0 字节& set /a FAIL+=1)
) else (
    echo  [FAIL] 代理请求 HTTP !PXYCODE!，收到 !PSIZE! 字节
    echo  --- serve_test.log ---
    type serve_test.log
    set /a FAIL+=1
)

rem 关掉测试用 serve.py（杀掉监听测试端口的进程）
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }" >nul 2>nul

rem ---------- 6. 前端同款解析 ----------
echo  用前端同款逻辑解析两份捕获：
python test_decode.py direct.txt proxied.txt
if errorlevel 1 (echo  [FAIL] 解析出的事件为空& set /a FAIL+=1) else (echo  [PASS] 事件解析正常& set /a PASS+=1)

rem ---------- 结论 ----------
del /q health.tmp page_code.tmp proxy_code.tmp 2>nul
echo.
echo ==============================================
echo  结论: PASS !PASS! / FAIL !FAIL!
echo ==============================================
if !FAIL! gtr 0 goto fail_summary
goto pass_summary

:fail_summary
echo  把上面 FAIL 项和输出截图发给开发者。
echo  常见原因：
echo   - 第 3 步失败: 后端起不来，看「云游-后端」窗口里的报错
echo   - 第 4 步失败: 后端本身没吐数据
echo   - 第 5 步失败: serve.py 代理问题（旧版本 / 防火墙 / 代理软件）
echo   - 第 6 步失败: 数据格式异常
goto summary_done

:pass_summary
echo  数据链路正常！浏览器仍收不到时：
echo   1. 关掉旧的前端窗口，重新运行 run.bat（用最新 serve.py）
echo   2. 浏览器 Ctrl+F5 强制刷新（旧 JS 缓存有丢数据的 bug）
echo   3. 还不行就按 F12 打开开发者工具，看 Network 里 /web 请求的状态码和响应
goto summary_done

:summary_done
echo.
echo  捕获文件保存在 direct.txt 和 proxied.txt，可打开查看。
echo  若后端由本脚本拉起，测试后仍在运行（不需要可关闭该窗口）。
pause

@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo  ==============================================
echo   云游 Wander - 一键启动 (Agent 后端 + Web 前端)
echo  ==============================================
echo.

rem ---------- 1. 检查 Python 环境 ----------
where python >nul 2>nul
if errorlevel 1 (
    echo  [错误] 未检测到 Python。请先安装 Python 3.12 及以上版本，
    echo         安装时勾选 "Add python.exe to PATH"：
    echo         https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('python -c "import sys;print(sys.version.split()[0])"') do set "PYVER=%%v"
python -c "import sys;sys.exit(0 if sys.version_info>=(3,12) else 1)" >nul 2>nul
if errorlevel 1 (
    echo  [错误] Python 不可用或版本过低 ^(!PYVER!^)，本项目需要 3.12 及以上。
    echo         若刚装好 Python 仍报错，可能是 Microsoft Store 的占位程序，
    echo         请从 https://www.python.org/downloads/ 安装并勾选 "Add python.exe to PATH"。
    echo.
    pause
    exit /b 1
)
echo  [OK] Python !PYVER!

rem ---------- 2. 检查 .env 环境变量 ----------
if not exist .env (
    echo  [错误] 未找到 .env 配置文件。
    if exist .env.example (
        echo         请先复制 .env.example 为 .env，并填入你的 API Key：
        echo           copy .env.example .env
        echo           notepad .env
    )
    echo.
    pause
    exit /b 1
)

set "MISSING="
set "DEEPSEEK_API_KEY="
set "DEEPSEEK_API_BASE="
set "DEEPSEEK_MODULE_NAME="
for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env") do (
    if /i "%%a"=="DEEPSEEK_API_KEY" set "DEEPSEEK_API_KEY=%%b"
    if /i "%%a"=="DEEPSEEK_API_BASE" set "DEEPSEEK_API_BASE=%%b"
    if /i "%%a"=="DEEPSEEK_MODULE_NAME" set "DEEPSEEK_MODULE_NAME=%%b"
)
if not defined DEEPSEEK_API_KEY set "MISSING=!MISSING! DEEPSEEK_API_KEY"
if not defined DEEPSEEK_API_BASE set "MISSING=!MISSING! DEEPSEEK_API_BASE"
if not defined DEEPSEEK_MODULE_NAME set "MISSING=!MISSING! DEEPSEEK_MODULE_NAME"
if defined MISSING (
    echo  [错误] .env 中缺少以下环境变量：!MISSING!
    echo         请参考 .env.example 补齐后重新运行。
    echo.
    pause
    exit /b 1
)
echo  [OK] .env 环境变量检查通过

rem ---------- 3. 安装 Python 依赖（pip，来自 pyproject.toml） ----------
python -c "import fastapi,uvicorn,openai,dotenv,pydantic,httpx,requests,liteq,botpy" >nul 2>nul
if errorlevel 1 (
    echo  [*] 首次运行，正在用 pip 安装 pyproject.toml 中的依赖，请稍候 ...
    python -c "import tomllib,subprocess,sys;d=tomllib.load(open('pyproject.toml','rb'))['project']['dependencies'];sys.exit(subprocess.call([sys.executable,'-m','pip','install']+d))"
    if errorlevel 1 (
        echo.
        echo  [错误] 依赖安装失败。请检查网络后重试，或手动执行：
        echo         python -m pip install fastapi uvicorn openai python-dotenv pydantic httpx requests liteq qq-botpy
        echo.
        pause
        exit /b 1
    )
)
echo  [OK] Python 依赖就绪

rem ---------- 4. 检查前端产物 ----------
if exist "web\dist\index.html" (
    echo  [OK] 前端页面已编译 (web\dist)
) else (
    echo  [警告] 未找到编译好的前端页面 (web\dist)。
    echo         前端界面将无法打开。如需编译，请安装 Node.js 后在项目根目录执行：
    echo           cd web ^&^& npm install ^&^& npm run build
)

rem ---------- 5. 启动 ----------
set "AGENT_PORT="
for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env") do (
    if /i "%%a"=="agent_port" set "AGENT_PORT=%%b"
)
if not defined AGENT_PORT set "AGENT_PORT=3000"

echo.
echo  [*] 启动后端   http://127.0.0.1:!AGENT_PORT!
start "云游-后端 (Agent)" cmd /k "python main.py"
echo  [*] 启动前端   http://localhost:8000
start "云游-前端 (Web)" cmd /k "set AGENT_BACKEND=http://127.0.0.1:!AGENT_PORT!&& python serve.py"

rem 等两个服务起来后自动打开浏览器
timeout /t 3 /nobreak >nul
start "" http://localhost:8000

echo.
echo  启动完成！浏览器将自动打开 http://localhost:8000
echo  关闭对应窗口即可停止服务；重新运行本脚本可再次启动。
echo.
pause

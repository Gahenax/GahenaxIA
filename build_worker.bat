@echo off
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
cd OEDA_HodgeRigidity\tools\mersenne-worker-rs
echo Cleaning target...
cargo clean
echo Building in release mode...
cargo build --release



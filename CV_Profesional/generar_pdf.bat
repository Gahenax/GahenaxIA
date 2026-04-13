@echo off
set "HTML_FILE=%~dp0cv_prototipo.html"
set "PDF_FILE=%~dp0CV_Jotam_Profesional.pdf"

set "EDGE_PATH="
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    set "EDGE_PATH=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    set "EDGE_PATH=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

if defined EDGE_PATH (
    echo Generando PDF con Microsoft Edge...
    "%EDGE_PATH%" --headless --print-to-pdf="%PDF_FILE%" --no-pdf-header-footer "%HTML_FILE%"
    echo PDF generado con exito en: %PDF_FILE%
) else (
    echo No se encontro Microsoft Edge para generar el PDF.
)
pause

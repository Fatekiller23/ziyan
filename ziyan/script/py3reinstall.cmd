title py2reinstall-ziyan
py -3 -m pip uninstall -y ziyan 1>nul
cd ../..
if exist build rm -r build
echo 'clean build/'
py -3 setup.py install 1>nul
echo 'py -3 reinstall good'
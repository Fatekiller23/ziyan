title reinstall-ziyan
pip uninstall -y ziyan 1>nul
cd ../..
python setup.py install 1>nul
echo 'good'
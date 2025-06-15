```
$f = "$env:TEMP\add_app.py"
Invoke-WebRequest "https://raw.githubusercontent.com/DuyNguyen2k6/CV/main/add%20app.py" -OutFile $f
python $f
```

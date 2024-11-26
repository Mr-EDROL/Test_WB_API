### Before start:

1. Copy .json of your Google service account to folder ```.\secret```

2. Create file
```.env```
```
WB_API_TOKEN=############################
GOOGLE_CREDENTIALS_FILE=.\secret\###.json
```

3. Run
```
pip install -r requirements.txt
```

### To start
Run
```
python3 -m WB_API.py
```
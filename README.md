# ClientServer
PHẦN MỀM DOWNLOAD / UPLOAD FILE DÙNG KỸ THUẬT ĐA LUỒNG, KẾT NỐI BẰNG TCP

![alt text](https://github.com/doanxem99/ClientServer/blob/main/assets/image2.jpg?raw=true)

# User
---

## Usage

### 1. Client

1. You can download in release package or clone this repository:
```
git clone https://github.com/doanxem99/ClientServer.git
```
2. Go to folder dist and click main.exe
3. Enjoy :>

### 2. Server
Open terminal and run this command:
```
python server.py
```

---

# Developer
---

## 1. Environment

You should create virtual environment for easier remove when not needed.

To install python virtual environment

**Window**
```
python -m pip install --user virtualenv
python -m venv env
cd env
git clone https://github.com/doanxem99/ClientServer.git
pip install -r requirements.txt
```
**Linux** (* is version of python)
```
sudo apt install python3-tk
sudo apt install python*-venv
python -m venv env
cd env
git clone https://github.com/doanxem99/ClientServer.git
pip install -r requirements.txt
```

## 2. Usage

### 2.1 Client

1. Open terminal and go to virtual environment folder
2. Use this command to activate virtual environment:

**Window**
```
call env\Scripts\activate
```
**Linux**
```
source env/bin/activate
```

3. Run this command to start client GUI:
```
python main.py
```

### 2.2 Server

1. Open terminal and go to virtual environment folder
2. Use this command to activate virtual environment:

1. Open terminal and go to virtual environment folder
2. Use this command to activate virtual environment:

**Window**
```
call env\Scripts\activate
```
**Linux**
```
source env/bin/activate
```

3. Run this command to start server:
```
python server.py
```

   

    
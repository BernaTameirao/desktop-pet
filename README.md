# Desktop Pet

**Desktop Pet** is a small **Python + PyQt5** desktop application that brings animated pets to your screen.  
They walk, jump and can even be dragged with your mouse — all in real time!

---

## Features

- Pets that move naturally across your desktop  
- Jumping and falling animations with simulated gravity  
- Smooth visual effects
- Click and drag interaction  
- Multi-monitor support  

---

## Technologies Used

- [Python 3.10+](https://www.python.org/)
- [PyQt5](https://pypi.org/project/PyQt5/)

---

## Project Structure

```
desktop-pet/
├── src/
│   ├── main.py
│   └── Pet.py
├── notebooks/
│   └── Pet.ipynb
├── imgs/
├── requirements.txt
└── README.md
```

> Each pet should have its images in the format:  
> `name_0.png`, `name_1.png`, `name_2.png`, etc.

---

## How to Run

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python main.py
```

Three pets will appear on your desktop.  
They will move automatically, and you can drag them around or interact with them using the mouse.

---

## Requirements

- Python 3.10 or higher  
- Operating System: Windows, macOS, or Linux  
- Dependencies listed in `requirements.txt`

---
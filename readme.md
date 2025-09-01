# Backend Project Coderr - a freelance developer platform

This is the backend for a Django REST API application.  
The project is based on Django and Django REST Framework and uses a classic app structure (e.g. app_auth, ...).  
With this API you can manage user authentication, boards, and tasks.  

---

## Project Structure

> backend/.  
> ── app_auth/<br>  
> ── app_meta/<br>  
> ── app_offers/<br>  
> ── app_orders/<br>  
> ── app_reviews/<br>  
> ── core/<br>  
> ── env/                  # local virtual environment (ignored)<br>  
> ── manage.py<br>  
> ── requirements.txt<br>  
> ── .gitignore<br>  

---

## Requirements

- **Python 3.8+**  
- **pip**  
- Optional: **virtualenv**  

---

## Installation

1. **Clone the repository**  
git clone https://github.com/<your-username>/<repo-name>.git  
cd <repo-name>  

2. **Create a virtual environment**  
python -m venv env  
source env/bin/activate   # Windows: env\Scripts\activate  

3. **Install dependencies**  
pip install -r requirements.txt  

4. **Run migrations**  
python manage.py migrate  

5. **Create a superuser for the admin**  
python manage.py createsuperuser  

6. **Start the server**  
python manage.py runserver  

> **Note:**  
> By default, the server runs at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
> Adjust `core/settings.py` for databases, `DEBUG`, and `ALLOWED_HOSTS` as needed.  

---

## Dependencies (`requirements.txt`)

- `Django`  
- `djangorestframework`  
- `django-cors-headers`
- `django-filter`
- `sqlparse`

---

## Security

- Make sure `.env` files are **not** pushed to the repo (see `.gitignore`).  
- Do not commit database files (`*.sqlite3`).  
- Use `.env` exclusively for secret keys and passwords.  

---

## License

MIT License – see [LICENSE](LICENSE)  

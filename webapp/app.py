import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, Response, request, send_file, make_response, url_for
import threading
import time
import json
from datetime import date
from sqlalchemy import func
from db.database import SessionLocal
from db.models import News
from processor import run_pipeline_main
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pdfkit
import tempfile
import uuid


app = Flask(__name__)

progress_data = {"progress": 0, "message": "Очікування запуску..."}

def has_today_news():
    session = SessionLocal()
    try:
        today = date.today()
        return session.query(News).filter(News.Date == today).count() > 0
    finally:
        session.close()

def generate_progress():
    while True:
        time.sleep(0.5)
        data = json.dumps(progress_data)
        yield f"data: {data}\n\n"
        if progress_data["progress"] >= 100:
            break

def update_progress(message, progress):
    progress_data["message"] = message
    progress_data["progress"] = progress

def pipeline_thread(sources, telegram_channels):
    run_pipeline_main(update_progress, sources=sources, telegram_channels=telegram_channels)
    update_progress("Обробка завершена!", 100)

@app.route("/")
def index():
    session = SessionLocal()
    try:
        today_news = has_today_news()
        available_dates = session.query(News.Date).group_by(News.Date).all()
        date_list = [d[0].isoformat() for d in available_dates if d[0] is not None]
    finally:
        session.close()

    return render_template("index.html", has_news=today_news, available_dates=date_list)

@app.route("/start", methods=["POST"])
def start():
    data = request.get_json()
    sources = data.get("sources", [])
    telegram_channels = data.get("telegram_channels", [])

    thread = threading.Thread(target=pipeline_thread, args=(sources, telegram_channels))
    thread.start()
    return "", 204

@app.route("/progress")
def progress():
    return Response(generate_progress(), mimetype="text/event-stream")

@app.route("/news")
def show_news():
    session = SessionLocal()
    today = date.today()
    try:
        if not has_today_news():
            available_dates = session.query(News.Date).group_by(News.Date).all()
            date_list = [d[0].isoformat() for d in available_dates if d[0] is not None]
            return render_template("news.html", news=[], selected_date=today.isoformat(),
                                   available_dates=date_list, current_date=today.isoformat())

        news_list = session.query(News).filter(News.Date == today).order_by(News.Date.desc()).all()
        available_dates = session.query(News.Date).group_by(News.Date).all()
        date_list = [d[0].isoformat() for d in available_dates if d[0] is not None]
    finally:
        session.close()

    return render_template("news.html", news=news_list, selected_date=today.isoformat(),
                           available_dates=date_list, current_date=today.isoformat())

@app.route("/news/<int:news_id>")
def single_news(news_id):
    session = SessionLocal()
    news_item = session.query(News).filter(News.id == news_id).first()
    available_dates = session.query(News.Date).distinct().all()
    available_dates = [d[0].isoformat() for d in available_dates]
    session.close()

    return render_template("single_news.html", news=news_item, available_dates=available_dates)

@app.route("/news/<selected_date>")
def news_by_date(selected_date):
    session = SessionLocal()
    try:
        news_list = session.query(News).filter(News.Date == selected_date).all()
        available_dates = session.query(News.Date).group_by(News.Date).all()
        date_list = [d[0].isoformat() for d in available_dates if d[0] is not None]
    finally:
        session.close()

    return render_template("news.html", news=news_list, selected_date=selected_date,
                           available_dates=date_list, current_date=date.today().isoformat())


@app.route("/news/report/<report_date>")
def download_report(report_date):
    session = SessionLocal()
    try:
        news_list = session.query(News).filter(News.Date == report_date).all()
        available_dates = session.query(News.Date).group_by(News.Date).all()
        date_list = [d[0].isoformat() for d in available_dates if d[0] is not None]
    finally:
        session.close()

    # Рендеримо шаблон без графіка
    rendered = render_template(
        "report_template.html",
        news=news_list,
        date=report_date,
        available_dates=date_list
    )

    # Конфігурація PDF
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    options = {
        'enable-local-file-access': None
    }

    pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=report_{report_date}.pdf'
    return response




if __name__ == "__main__":
    app.run(debug=True, threaded=True)

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    titel = Column(String, nullable=False)
    firma = Column(String)
    ort = Column(String)
    beschreibung = Column(Text)
    url = Column(String)
    quelle = Column(String, default='manuell')  # adzuna, stepstone, linkedin, foto-upload, manuell
    status = Column(String, default='neu')
    notiz = Column(Text)
    gehalt_min = Column(Integer)
    gehalt_max = Column(Integer)
    bewerbungsfrist = Column(DateTime)
    ist_remote = Column(Boolean, default=False)
    ist_hybrid = Column(Boolean, default=False)
    sprache = Column(String, default='de')
    tags = Column(Text)  # JSON-Array als String
    skill_gap_score = Column(Float)
    skill_gap_json = Column(Text)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    aktualisiert_am = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    applications = relationship('Application', back_populates='job')

class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    status = Column(String, default='beworben')
    bewerbungsdatum = Column(DateTime, default=datetime.utcnow)
    gespraechstermin = Column(DateTime)
    notiz = Column(Text)
    absage_text = Column(Text)
    anschreiben = Column(Text)
    anschreiben_score = Column(Float)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    job = relationship('Job', back_populates='applications')
    status_logs = relationship('ApplicationStatusLog', back_populates='application')

class ApplicationStatusLog(Base):
    __tablename__ = 'application_status_logs'
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
    status = Column(String)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    application = relationship('Application', back_populates='status_logs')

class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    titel = Column(String, nullable=False)
    faellig_am = Column(DateTime)
    erledigt = Column(Boolean, default=False)
    mail_sent = Column(Boolean, default=False)
    wiederholung = Column(String)  # daily, weekly, monthly, None
    erstellt_am = Column(DateTime, default=datetime.utcnow)

class SearchProfile(Base):
    __tablename__ = 'search_profiles'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    suchbegriff = Column(String)
    ort = Column(String)
    radius_km = Column(Integer, default=25)
    portale = Column(Text)  # JSON-Array
    aktiv = Column(Boolean, default=True)
    letzter_lauf = Column(DateTime)
    erstellt_am = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True)
    theme = Column(String, default='dark')
    language = Column(String, default='de')
    ai_model = Column(String, default='mistral')
    ai_tone = Column(String, default='formell')
    ai_language = Column(String, default='auto')  # auto, de, en
    default_location = Column(String)
    default_radius_km = Column(Integer, default=25)
    hide_ausbildung = Column(Boolean, default=True)
    reminder_default_days = Column(Integer, default=7)
    color_blind_mode = Column(String, default='none')
    onboarding_done = Column(Boolean, default=False)
    backup_path = Column(String, default='./backups')
    backup_enabled = Column(Boolean, default=True)
    wochenziel = Column(Integer, default=5)
    # verschluesselte API-Keys
    adzuna_app_id_enc = Column(Text)
    adzuna_api_key_enc = Column(Text)
    linkedin_api_key_enc = Column(Text)
    arbeitsagentur_client_id_enc = Column(Text)
    arbeitsagentur_client_secret_enc = Column(Text)
    smtp_host = Column(String)
    smtp_port = Column(Integer, default=587)
    smtp_user = Column(String)
    smtp_password_enc = Column(Text)
    smtp_recipient = Column(String)

class CoverLetterTemplate(Base):
    __tablename__ = 'cover_letter_templates'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, default='allgemein')  # IT, Pflege, Handwerk, Buero, Logistik
    body = Column(Text, nullable=False)  # mit {stelle}, {firma}, {ort}, {datum}, {anrede}
    is_custom = Column(Boolean, default=False)
    sprache = Column(String, default='de')
    erstellt_am = Column(DateTime, default=datetime.utcnow)

class Blocklist(Base):
    __tablename__ = 'blocklist'
    id = Column(Integer, primary_key=True)
    firma = Column(String)
    recruiter_name = Column(String)
    grund = Column(Text)
    erstellt_am = Column(DateTime, default=datetime.utcnow)

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    firma = Column(String)
    rolle = Column(String)
    email = Column(String)
    telefon = Column(String)
    linkedin_url = Column(String)
    notizen = Column(Text)
    naechster_kontakt = Column(DateTime)
    erstellt_am = Column(DateTime, default=datetime.utcnow)

class UserBadge(Base):
    __tablename__ = 'user_badges'
    id = Column(Integer, primary_key=True)
    badge_key = Column(String, unique=True)  # erste_bewerbung, streak_7, etc.
    freigeschaltet_am = Column(DateTime, default=datetime.utcnow)

class BackupLog(Base):
    __tablename__ = 'backup_logs'
    id = Column(Integer, primary_key=True)
    dateiname = Column(String)
    groesse_bytes = Column(Integer)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    erfolgreich = Column(Boolean, default=True)

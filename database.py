from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with sample data"""
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        #from models import User
        #admin = User.query.filter_by(username='admin').first()
        #if not admin:
            #admin = User(
                #username='admin',
                #email='admin@school.edu',
                #full_name='System Administrator',
                #role='admin'
            #)
            #admin.set_password('admin123')
            #db.session.add(admin)
            #db.session.commit()
            #print("Default admin user created:")
            #print("Username: admin")
            #print("Password: admin123")
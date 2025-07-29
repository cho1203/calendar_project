from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("데이터베이스 테이블이 생성되었습니다.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
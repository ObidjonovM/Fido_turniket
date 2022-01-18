from app import app




if __name__ == '__main__':
    app.run(host='10.50.50.212', port=5080, debug=True, ssl_context='adhoc')

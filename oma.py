#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, session, redirect, url_for, escape, request, Response, render_template, make_response
import os
import sqlite3
import logging
import sys
import json
from functools import wraps
from contextlib import closing

logging.basicConfig(filename=os.path.abspath('../../piilo/flask.log'),level=logging.DEBUG)

app = Flask(__name__)
app.debug = True



# Aliohjelma elokuvien hakemiselle tietokannasta
@app.route('/haeElokuvat', methods=['GET'])
def haeElokuvat():
    db = connect_db()
    elokuvat = []
    try:
        sql = """
        SELECT *
        FROM Elokuva
        """
        cur = db.execute(sql)
        for row in cur.fetchall():
            elokuvat.append( dict(ElokuvaID=row[0], ElokuvaNimi=row[1]) )
    except Exception as e:
        logging.debug(str(e))
        elokuvat = ""
    db.close()

    resp = make_response( render_template("elokuvat.xml", elokuvat=elokuvat) )
    resp.charset = "UTF-8"
    resp.mimetype = "application/json"

    return resp

@app.route('/haeJasenet', methods=['GET'])
def haeJasenet():
    db = connect_db()
    jasenet =[]
    try:
        sql = """
        SELECT *
        FROM Jasen
        """

        cur = db.execute(sql)
        for row in cur.fetchall():
            jasenet.append( dict(JasenID=row[0], JasenNimi=row[1]) )
    except Exception as e:
        logging.debug(str(e))
        jasenet = ""
    db.close()

    resp = make_response( render_template("jasenet.xml", jasenet=jasenet) )
    resp.chartset = "UTF-8"
    resp.mimetype = "application/json"

    return resp

#Aliohjelma vuokraustaulun täydentämiseen.
@app.route('/haeVuokraukset', methods=['GET'])
def haeVuokraukset():
    db = connect_db()
    vuokraukset = []
    jasenet = []
    elokuvat = []

    try:
        sql = """
        SELECT *
        FROM Vuokraus
        ORDER BY VuokrausPVM
        """

        cur = db.execute(sql)

        for row in cur.fetchall():
            vuokraukset.append( dict(JasenID=row[0], ElokuvaID=row[1], VuokrausPVM=row[2], PalautusPVM=row[3], Maksettu=row[4]) )

        sql = """
        SELECT ElokuvaID, Nimi
        FROM Elokuva
        """

        cur = db.execute(sql)

        for row in cur.fetchall():
            elokuvat.append( dict(ElokuvaID=row[0], Nimi=row[1]) )

        sql = """
        SELECT JasenID, Nimi
        FROM Jasen
        """

        cur = db.execute(sql)

        for row in cur.fetchall():
            jasenet.append( dict(JasenID=row[0], JasenNimi=row[1]) )

    except Exception as e:
        logging.debug(str(e))
        vuokraukset = ""

    db.close()

    resp = make_response( render_template("vuokraukset.xml", vuokraukset=vuokraukset, elokuvat=elokuvat, jasenet=jasenet) )
    resp.charset = "UTF-8"
    resp.mimetype = "application/json"

    return resp

@app.route('/lisaaVuokraus', methods=['POST', 'GET'])
def lisaaVuokraus():
    db = connect_db()

    try:
        JasenID = request.form['JasenNimi']
        ElokuvaID = request.form['ElokuvaNimi']
        VuokrausPVM = request.form['VuokrausPVM']
        PalautusPVM = request.form['PalautusPVM']
        Maksettu = request.form['Maksettu']

        sql = """
        INSERT INTO Vuokraus (JasenID, ElokuvaID, VuokrausPVM, PalautusPVM, Maksettu)
        VALUES (?,?,?,?,?)
        """

        cur = db.execute(sql, (JasenID, ElokuvaID, VuokrausPVM, PalautusPVM, Maksettu))
        db.commit()

    except Exception as e:
        logging.debug(sys.exc_info()[0])
        logging.debug(str(e))

    db.close()

    return "Lisätty."
    
#SQL yhteyden muodostus
def connect_db():
    try:
        con = sqlite3.connect(os.path.abspath('../../piilo/video'))
        con.row_factory = sqlite3.Row
        logging.debug("Tietokantayhteys muodostettu.")
    except Exception as e:
        logging.debug("Kanta ei aukea.")
        logging.debug(str(e))
    return con


if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)

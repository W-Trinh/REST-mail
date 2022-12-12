from flask import Flask, jsonify, abort, request
import mariadb
import urllib.parse

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False  # pour utiliser l'UTF-8 plutot que l'unicode


def execute_query(query, data=()):
    config = {
        'host': 'mariadb',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'mydatabase'
    }
    """Execute une requete SQL avec les param associés"""
    # connection for MariaDB
    conn = mariadb.connect(**config)
    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute(query, data)

    if cur.description:
        # serialize results into JSON
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        list_result = []
        for result in rv:
            list_result.append(dict(zip(row_headers, result)))
        return list_result
    else:
        conn.commit()
        return cur.lastrowid


# we define the route /
@app.route('/')
def welcome():
    liens = [{}]
    liens[0]["_links"] = [{
        "href": "/mailboxes",
        "rel": "mailboxes"
    }]
    return jsonify(liens), 200

@app.route('/mailboxes', methods=['POST'])
def post_mailboxes():
    "Créer une bal en fournissant un nom d'utilisateur (son futur identifiant)"
    user_name = request.args.get("name")
    execute_query("insert into users (name) values (?)", (user_name,))
    execute_query("insert into mailboxes (user_id) values  ( (select id from users where name = ?) )", (user_name,))
    # on renvoi le lien du mailboxes  que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/mailboxes/" + user_name,
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created

@app.route('/mailboxes/<string:user_name>', methods=['DELETE'])
def delete_mailboxes(user_name):
    "Supprimer une bal en fournissant son nom"
    user = execute_query("select id from users where name = ?", (user_name,))
    if user == []:
        abort(404, "Cet utilisateur n'existe pas")

    execute_query("delete from mailboxes where user_id = ?", (user[0]["id"],))
    execute_query("delete from users where name = ?", (user_name,))

    return "",204  # no data

if __name__ == '__main__':
    # define the localhost ip and the port that is going to be used
    app.run(host='0.0.0.0', port=5000)

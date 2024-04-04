title: Debug
date: 2024-03-25
template: page_debug_info.html
navbar: True
requires_login: True
form: False
---

# App Debug Info 

<!-- Button trigger modal -->
<button type="button" class="btn btn-primary" data-toggle="modal" data-target="#configInfoModal">
  Show some app intergal settings
</button>

<!-- Modal -->
<div class="modal fade" id="configInfoModal" tabindex="-1" role="dialog" aria-labelledby="configInfoModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title" id="configInfoModalLabel">Dump of g.pdata.__dict__ </h3>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        {% if g.pdata is not none %}
          {% for k in g.pdata.__dict__ %}
            {{ k }} = {{ g.pdata.__dict__[k] }} <br>
          {% endfor %}
        {% endif %}
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        <!-- <button type="button" class="btn btn-primary">Save changes</button> -->
      </div>
    </div>
  </div>
</div>

# Working Installation requirements.txt

<!-- Button trigger modal -->
<button type="button" class="btn btn-primary" data-toggle="modal" data-target="#requirementsModal">
  Dump of `pip freeze`
</button>

<!-- Modal -->
<div class="modal fade" id="requirementsModal" tabindex="-1" role="dialog" aria-labelledby="requirementsModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title" id="requirementsModalLabel">Dump pip freeze </h3>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
```
#begin [cat /tmp/tmpug_4i1iw] [1712272899.241654] > /tmp/tmp_aa2dl8p
#begin [pip freeze] [1712272896.980654] <a href="/stream?q=cat+/tmp/tmpug_4i1iw" class="btn btn-link" role="button">/tmp/tmpug_4i1iw</a>
WARNING: The directory '/home/app/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
DEPRECATION: Loading egg at /usr/local/lib/python3.11/site-packages/PIL-1.1.7-py3.11.egg is deprecated. pip 24.3 will enforce this behaviour change. A possible replacement is to use pip for package installation.. Discussion can be found at https://github.com/pypa/pip/issues/12330
alembic==1.13.1
aniso8601==9.0.1
blinker==1.7.0
Brotli==1.1.0
cachelib==0.9.0
click==8.1.7
dominate==2.9.1
Flask @ file:///wheels/flask-3.0.2-py3-none-any.whl#sha256=3232e0e9c850d781933cf0207523d1ece087eb8d87b23777ae38456e2fbe7c6e
Flask-Admin @ file:///wheels/Flask_Admin-1.6.1-py3-none-any.whl#sha256=fd8190f1ec3355913a22739c46ed3623f1d82b8112cde324c60a6fc9b21c9406
Flask-Assets @ file:///wheels/Flask_Assets-2.1.0-py3-none-any.whl#sha256=a56c476b15f84701712cc3b4b4a001ebbe62b1dcbe81c23f96fbe6f261b75324
Flask-Bootstrap @ file:///wheels/Flask_Bootstrap-3.3.7.1-py3-none-any.whl#sha256=5eca70c8e457ada68d066ba38b472f87bdee8b119662658a0eb66a6aeec317e5
Flask-Caching @ file:///wheels/Flask_Caching-2.1.0-py3-none-any.whl#sha256=f02645a629a8c89800d96dc8f690a574a0d49dcd66c7536badc6d362ba46b716
Flask-Compress @ file:///wheels/Flask_Compress-1.14-py3-none-any.whl#sha256=b86c9808f0f38ea2246c9730972cf978f2cdf6a9a1a69102ba81e07891e6b26c
Flask-FlatPages @ file:///wheels/Flask_FlatPages-0.8.2-py3-none-any.whl#sha256=d638d05b8cde4498da3259f04e8b44e213bc0b113809ee5991b5ca16336ee771
Flask-Gravatar @ file:///wheels/Flask_Gravatar-0.5.0-py2.py3-none-any.whl#sha256=93be048a58cef92345e7bfc78e918e7f4c729b3a33646510b71948c024e7f591
Flask-HTTPAuth @ file:///wheels/Flask_HTTPAuth-4.8.0-py3-none-any.whl#sha256=a58fedd09989b9975448eef04806b096a3964a7feeebc0a78831ff55685b62b0
Flask-Images @ file:///wheels/Flask_Images-3.0.2-py3-none-any.whl#sha256=06db73b2218ff4fe5f66586b641f32b1df8ab32874167af1c9cc2299779eec0e
Flask-Login @ file:///wheels/Flask_Login-0.6.3-py3-none-any.whl#sha256=849b25b82a436bf830a054e74214074af59097171562ab10bfa999e6b78aae5d
Flask-Mail @ file:///wheels/Flask_Mail-0.9.1-py3-none-any.whl#sha256=149d15f93075a2f322e72d16ee1c6e0fdd093ce001a3a03e63bc30a648b8223b
Flask-Migrate @ file:///wheels/Flask_Migrate-4.0.7-py3-none-any.whl#sha256=5c532be17e7b43a223b7500d620edae33795df27c75811ddf32560f7d48ec617
Flask-PageDown @ file:///wheels/Flask_PageDown-0.4.0-py3-none-any.whl#sha256=aa6f938b5e809b6ef6889d28fef7096f20a0700de01082b0342764a5058225d2
Flask-Principal @ file:///wheels/Flask_Principal-0.4.0-py3-none-any.whl#sha256=72fdc95ea825ad30d8b307a7f1163f777daae0516273a41000749041b32f3742
flask-redis @ file:///wheels/flask_redis-0.4.0-py2.py3-none-any.whl#sha256=8d79eef4eb1217095edab603acc52f935b983ae4b7655ee7c82c0dfd87315d17
Flask-RESTful @ file:///wheels/Flask_RESTful-0.3.10-py2.py3-none-any.whl#sha256=1cf93c535172f112e080b0d4503a8d15f93a48c88bdd36dd87269bdaf405051b
Flask-Script @ file:///wheels/Flask_Script-2.0.6-py3-none-any.whl#sha256=9904e42da6e7cffa8b270f159a560e2771406a49f5d4d98a0e30eb0e9ffb7966
Flask-SeaSurf @ file:///wheels/Flask_SeaSurf-1.1.1-py3-none-any.whl#sha256=f70e58b3b5e8fa9a928fe6b8e7a01b953d67cb9b7bde1a54d1ec95e40fcc2ade
Flask-Session @ file:///wheels/flask_session-0.8.0-py3-none-any.whl#sha256=5dae6e9ddab334f8dc4dea4305af37851f4e7dc0f484caf3351184001195e3b7
Flask-SQLAlchemy @ file:///wheels/flask_sqlalchemy-3.1.1-py3-none-any.whl#sha256=4ba4be7f419dc72f4efd8802d69974803c37259dd42f3913b0dcf75c9447e0a0
Flask-SSLify @ file:///wheels/Flask_SSLify-0.1.5-py3-none-any.whl#sha256=fc381812e042a00acc96573af8c94e1eeb44952226300f73abd2e3428e5407ca
Flask-Uploads @ file:///wheels/Flask_Uploads-0.2.1-py3-none-any.whl#sha256=665323245dcbe9856f8ba2061fc91f41510630a1a15bfdb866d1815a9a8dec3f
Flask-WTF @ file:///wheels/flask_wtf-1.2.1-py3-none-any.whl#sha256=fa6793f2fb7e812e0fe9743b282118e581fb1b6c45d414b8af05e659bd653287
greenlet==3.0.3
gunicorn @ file:///wheels/gunicorn-21.2.0-py3-none-any.whl#sha256=3213aa5e8c24949e792bcacfc176fef362e7aac80b76c56f6b5122bf350722f0
itsdangerous==2.1.2
Jinja2==3.1.3
Mako==1.3.2
Markdown==3.6
MarkupSafe==2.1.5
msgspec==0.18.6
packaging==24.0
PIL==1.1.7
pillow==10.3.0
pillowcase==2.0.0
psycopg2-binary @ file:///wheels/psycopg2_binary-2.9.9-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl#sha256=143072318f793f53819048fdfe30c321890af0c3ec7cb1dfc9cc87aa88241de2
pytz==2024.1
PyYAML @ file:///wheels/PyYAML-6.0.1-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl#sha256=42f8152b8dbc4fe7d96729ec2b99c7097d656dc1213a3229ca5383f973a5ed6d
redis==5.0.3
six==1.16.0
SQLAlchemy==2.0.29
typing_extensions==4.10.0
visitor==0.1.3
webassets==2.0
Werkzeug==3.0.2
WTForms==3.1.2
#pid [28]
#end [pip freeze] > /tmp/tmpug_4i1iw
#pid [30]
#end [cat /tmp/tmpug_4i1iw] > /tmp/tmp_aa2dl8p
```
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        <!-- <button type="button" class="btn btn-primary">Save changes</button> -->
      </div>
    </div>
  </div>
</div>

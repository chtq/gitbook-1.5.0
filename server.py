#!/usr/bin/python
#coding=utf-8

import socket
import threading
import sys
import os
import MySQLdb
import base64
import hashlib
import struct
import string 
import subprocess
import time
import re
import commands
import urllib
import httplib
import json
import hashlib
# ====== config ======
COUNT = 0
HOST = 'localhost'
PORT = 3368
MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
      "Upgrade:websocket\r\n" \
      "Connection: Upgrade\r\n" \
      "Sec-WebSocket-Accept: {1}\r\n" \
      "WebSocket-Location: ws://{2}/chat\r\n" \
      "WebSocket-Protocol:chat\r\n\r\n"
class Th(threading.Thread):
  def __init__(self, connection):
    threading.Thread.__init__(self)
    self.con = connection
    self.DATA=''
    self.roottoken='NqTT2HZSs7-gJqp1RSR7'
    self.githost='166.111.132.191:10280'

  def gitpost(self, token, filename, username, host,context):
     #print 'heeeeeeeeee'
     conn = None
     print filename
     print username
     try:

	url = "/api/v3/projects/all?private_token={0}".format(token)
	conn = httplib.HTTPConnection(host)
	conn.request("GET", url)
        res=conn.getresponse()
        print res.status
        result= json.loads(res.read())
       # print result
       # conn.close()
        for i in range(len(result)):
            if result[i]["owner"]["name"]==username:
             # print result[i]
              headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
              value= urllib.urlencode({'file_path':filename, 'branch_name':'master', 'content':context, 'commit_message':'ks'})
              id =result[i]["id"]
              print id
              url1="/api/v3/projects/%d/repository/files?private_token=%s" %(id,token)
              print url1
              conn1 = httplib.HTTPConnection(host)
              conn1.request("POST", url1, value, headers)
              res1=conn1.getresponse()
              print res1.status
              if res1.status==400 and (filename.find('tk') or filename.find('wd')):
                 print "ffffffffffff"
                 conn1.request("PUT", url1, value, headers) 
              print  json.loads(res1.read())
              conn1.close()
     except Exception, e:
	print e
     finally:
	if conn:
	  conn.close()


  def execode(self, code): #对接收到的代码的操作
    global COUNT
    name = '%s%d.c' % (time.strftime('%Y-%m-%d', time.localtime(time.time())), COUNT)
    COUNT += 1
    outfile= open(name, 'wb')
    outfile.write(code)
    outfile.close()
    cmd = 'gcc %s -o %s.out' %(name, name) 
    status, outpout= commands.getstatusoutput(cmd)
    time.sleep(2)
    #cmd1 = "kill -9 %d" % int(p.pid)
   
    rmf2 = 'rm %s' %(name)
    print rmf2
    os.system(rmf2)

    if len(outpout)>0:
      self.send_data(outpout)
      return
    else:
      exe = './%s.out' %(name)
      #print exe
      status1, outpout1= commands.getstatusoutput(exe)
      data = outpout1
      #print data
      rmf1 = 'rm %s' %(exe)
      print rmf1
      os.system(rmf1)
    
    
    #f=subprocess.Popen(cmd,  shell=True, stdout=subprocess.PIPE)
    #time.sleep(10)
    #print f.poll()
    #if f.poll()==None:
      #print f.pid
   
    #kill_process_by_name("qemu")#杀掉进程,如果有多个同名进程这里有问题
    #data=f.stdout.readlines()
    
    #print "len:%d" %len(data)
    for i in range(len(data)):
      self.DATA+=re.sub('\n', '<br>', data[i])
    print self.DATA


  def run(self):
    print "run"

    s=self.recv_data(1024)
    print "receive :",s 
    if len(s)>4096:
      self.send_data("the code size is too long, must less 4k")
    else:
      com=s[0:2]
      print "com=%s" %com
      index=s.find('-')
      flag=s.find(';;;')
      print index
      if  (com =='wd' or com == 'tk'):
         chtqtoken='X1Ua_uPpyijshQX-gPDs'
         fname=s[2:index]
         username=s[index+1:flag]
         #print "fname=%s" % fname
         f=open('/tmp/'+fname, 'wb')
         f.write(s[index+1:])
         f.close()
         diff='diff %s %s' %('/tmp/'+fname, '/home/chtq/Downloads/test/'+com+fname+'/'+fname+'_answer.md')
         print diff
         dstatus, doutpout= commands.getstatusoutput(diff)
         doutpout=re.sub('\n', '<br>', doutpout)
         self.DATA=doutpout
         self.gitpost(self.roottoken, com+fname, username, self.githost, s[flag+3:])
      if(com=='xz'):
         
         fname=s[2:index]
         rname=fname.replace(r'/', '')
         username=s[index+1:flag]
         self.gitpost(self.roottoken, rname, username, self.githost, s[flag+3:])
         print s[flag+3:]
         if os.path.exists('/home/chtq/Downloads/test'+fname+'_answer.md'):
            f=open('/home/chtq/Downloads/test'+fname+'_answer.md')
            self.DATA=f.read()
      #else:
         #self.execode(s)
      #self.send_data(self.DATA)
 
  def recv_data(self, num):
    all_data=""
    self.con.setblocking(0)#非阻塞模式接受数据
    time.sleep(2)
    try:
      while 1:
        t = self.con.recv(num)
        print len(t)
        all_data+=t
        if len(t)<num:
          break
    except:
      return False
    else:#解码
      print ord(all_data[0])
      code_len = ord(all_data[1]) & 127
      if code_len == 126:
        masks = all_data[4:8] 
        len1=all_data[2:3]
        print "%x" %ord(all_data[2]) 
        print "%x" %ord(all_data[3])      
        data = all_data[8:]
      elif code_len == 127:
        masks = all_data[10:14]
        data = all_data[14:]
      else:
        masks = all_data[2:6]
        data = all_data[6:]
      raw_str = ""
      i = 0
      for d in data:
        raw_str += chr(ord(d) ^ ord(masks[i % 4]))
        i += 1
      return raw_str

  def send_data(self, data):
   # print data
    if data:
      data = str(data)
    else:
      return False
    token = "\x81"
    length = len(data)
    if length < 126:#编码
      token += struct.pack("B", length)
    elif length <= 0xFFFF:
      token += struct.pack("!BH", 126, length)
    else:
      token += struct.pack("!BQ", 127, length)
    data = '%s%s' % (token, data)
    self.con.send(data)
    return True

 # handshake
def handshake(con):
  headers = {}
  shake = con.recv(1024)
  
  if not len(shake):
   return False
  
  print shake

  header, data = shake.split('\r\n\r\n', 1)
  for line in header.split('\r\n')[1:]:
   key, val = line.split(': ', 1)
   headers[key] = val
  
  if 'Sec-WebSocket-Key' not in headers:
   print ('This socket is not websocket, client close.')
   con.close()
   return False
  
  sec_key = headers['Sec-WebSocket-Key']
  res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())
  
  str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', HOST + ':' + str(PORT))
  print str_handshake
  con.send(str_handshake)
  return True

def kill_process_by_name(name):

    cmd = "ps -e | grep %s" % name

    f = os.popen(cmd)

    txt = f.readlines()

    if len(txt) == 0:

        print "no process \"%s\"!!" % name

        return

    else:

       for line in txt:

         colum = line.split()

         pid = colum[0]

         cmd = "kill -9 %d" % int(pid)
         print cmd
         rc = os.system(cmd)
  
def new_service():
 """start a service socket and listen
 when coms a connection, start a new thread to handle it"""

 #print hashlib.new('md5',time.strftime('%Y-%m-%d:%H:%M:%S', time.localtime(time.time()))).hexdigest()
 #status, outpout= commands.getstatusoutput('gcc gg.c')
 #print "ddddd", outpout
 
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 try:
  sock.bind(('0.0.0.0', 3368))
  sock.listen(1000)
 
  print "bind 3368,ready to use"
 except:
  print("Server is already running,quit")
  sys.exit()
  
 while True:
  connection, address = sock.accept()

  print "Got connection from ", address
  if handshake(connection):#握手
   print "handshake success"
   try:
    t = Th(connection)
    t.start()

    print 'new thread for client ...'
   except:
    print 'start new thread error'
    connection.close()
    sock.close()
  
  
if __name__ == '__main__':
 new_service()

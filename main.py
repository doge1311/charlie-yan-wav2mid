import mido
from pylab import *
from math import *
import wave 
import struct
import sys
from matplotlib.pyplot import *

def read(str,de):
	try:
		val=int(input(str))
	except:
		val=de
	return val

filename=input("Input file name: ")
if len(filename.split('"'))==3:
	filename=filename.split('"')[1]

nt=read(str="Input note length (tick, 1/960 secs per tick) (Default: 20): ",de=20)
fft=read(str="Input FFT value (Default: 2400): ",de=2400)
lim=read(str="Input minimum vel (Default: 8): ",de=8)

ofn=filename+"_N"+str(nt)+"_F"+str(fft)+"_L"+str(lim)+".mid"
print("Output file: "+ofn)
print("Press enter to continue ...")
input()
print("Please wait...")
print("Reading WAV...")

wvf=wave.open(filename,"r")
nc=wvf.getnchannels()
sw=wvf.getsampwidth()
fr=wvf.getframerate()
nf=wvf.getnframes()

res=zeros(nf)

for i in range(nf):
	val=wvf.readframes(1)
	L=val[0:2]
	res[i]=struct.unpack('h',L)[0]

print("Generating FFT...")
FFt=specgram(res,NFFT=fft,Fs=fr,noverlap=(-1*fr/(960.0/nt))+fft)

pl=[]
now=440.0

for i in range(69,-1,-1):
	pl.append(now)
	now=now/(2**(1/12))


pl.reverse()
now=440.0

for i in range(70,128):
	now=now*(2**(1/12))
	pl.append(now)

go=[]

def itpp(lst,pos):
    ipos=int(pos)
    try:
        return lst[ipos]*(ipos+1-pos)+lst[ipos+1]*(pos-ipos)
    except IndexError:
        return 0

for i in range(len(FFt[0][0])):
	goo=[]
	fff=[]
	for j in range(len(FFt[0])):
		fff.append(FFt[0][j][i])
	for j in range(128):
		goo.append(sqrt(sqrt(itpp(fff,pl[j]/fr*fft)))*4)
	go.append(goo)

del FFt

print("Generating MIDI...")
mid=mido.MidiFile()
offl=[[],[],[],[],[],[],[],[]]
mid.add_track()
mid.add_track()
mid.add_track()
mid.add_track()
mid.add_track()
mid.add_track()
mid.add_track()
mid.add_track()
T1=mid.tracks[0]
T2=mid.tracks[1]
T3=mid.tracks[2]
T4=mid.tracks[3]
T5=mid.tracks[4]
T6=mid.tracks[5]
T7=mid.tracks[6]
T8=mid.tracks[7]
fstr=[0,0,0,0,0,0,0,0]
tc=[0,0,0,0,0,0,0,0]
cntnote=0
trs=[T1,T2,T3,T4,T5,T6,T7,T8]
for i in range(8):
	trs[i].append(mido.Message("program_change",program=78))

strs=".:!?*$#@"
allll=len(go)

for i in range(len(go)):
	strr=""
	if i%100==0:
		strr=str(int(i/allll*100000//1000))+"."+str(int(i/allll*100000)%1000).zfill(3)+'%\t'
	for j in range(128):
		vel=go[i][j]
		if vel>lim:
			strr=strr+strs[min(int(vel/2),127)//16]
			for k in range(8):
				if vel>32*k and vel<=32*(k+1):
					cntnote+=1
					m1,m2=0,0
					if fstr[k]:
						m1=tc[k]-nt
						m2=nt
						tc[k]=0
						fstr[k]=0
					trs[k].append(mido.Message("note_on",note=j,time=m1,velocity=min(int(vel/2),127)))
					offl[k].append(mido.Message("note_off",note=j,time=m2,velocity=min(int(vel/2),127)))
		else:
			strr=strr+" "
	if i%100==0:
		print(strr)
	for j in range(8):
		tc[j]+=nt
		trs[j].extend(offl[j])
		offl[j]=[]
		fstr[j]=1

(T1,T2,T3,T4,T5,T6,T7,T8)=trs
T1.append(mido.MetaMessage('end_of_track'))
T2.append(mido.MetaMessage('end_of_track'))
T3.append(mido.MetaMessage('end_of_track'))
T4.append(mido.MetaMessage('end_of_track'))
T5.append(mido.MetaMessage('end_of_track'))
T6.append(mido.MetaMessage('end_of_track'))
T7.append(mido.MetaMessage('end_of_track'))
T8.append(mido.MetaMessage('end_of_track'))
print("Notes: "+str(cntnote))
print("Outputting MIDI...")
mid.save(ofn)
print("Press enter to exit ...")
input()
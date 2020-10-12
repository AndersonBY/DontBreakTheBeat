# -*- coding: utf-8 -*-
# @Author: ander
# @Date:   2020-09-03 14:03:13
# @Last Modified by:   ander
# @Last Modified time: 2020-10-12 12:20:10
import librosa
import glob
from moviepy.editor import CompositeAudioClip, AudioFileClip
import moviepy.audio.fx.all as afx
import os


musics = glob.glob('./musics/*.mp3')

musics_beats = []
for music in musics:
	print(f'Loading {music}')
	y, sr = librosa.load(music)
	bpm, beats = librosa.beat.beat_track(y=y, sr=sr)
	beat_times = list(librosa.frames_to_time(beats, sr=sr))
	musics_beats.append((music, bpm, beat_times))

musics_beats.sort(key=lambda x: x[1])

music_clips = []
clip_times = []
final_clip_time = 0
for index, item in enumerate(musics_beats):
	music, bpm, beat_times = item
	clip_times.append((music, bpm, final_clip_time))
	music_clip = AudioFileClip(music)
	if index == 0:
		music_clip = music_clip.set_start(final_clip_time)
		final_clip_time += beat_times[-6]
	else:
		music_clip = music_clip.subclip(beat_times[0]).set_start(final_clip_time)
		final_clip_time += beat_times[-6] - beat_times[0]
	music_clip = music_clip.fx(afx.audio_fadeout, music_clip.duration - beat_times[-6])
	music_clip = music_clip.fx(afx.audio_fadein, beat_times[3])
	music_clips.append(music_clip)

with open('playlist.txt', 'w') as f:
	f.write('Time\tBPM\tName\n')
	for music, bpm, clip_time in clip_times:
		minutes, seconds = divmod(int(clip_time), 60)
		hours, minutes = divmod(minutes, 60)
		f.write(f'{hours}:{minutes:02d}:{seconds:02d}\t{int(bpm)}\t{os.path.basename(music)}\n')

final_clip = CompositeAudioClip(music_clips)
final_clip.fps = 44100
final_clip.write_audiofile('final.mp3', bitrate='320k')

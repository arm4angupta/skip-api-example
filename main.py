import json
import subprocess
import re

with open("deleted_sections.json", "r") as f:
    deleted_sections = json.load(f)

cmd = [ 'ffprobe', '-show_format', '-pretty', '-print_format', 'json', './test.mp3' ]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
out = json.loads(out.decode("utf8"))
duration = out['format']['duration']
hours, minutes, seconds = (duration.split(":")[0], duration.split(":")[1], duration.split(":")[2])
duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
print(f"Total File Duration: {duration}")
start_and_ends = []
base = f"ffmpeg -i test.mp3 -filter_complex \""
start = 0
end = duration
for i in range(len(deleted_sections)):
    section = deleted_sections[i]
    base += f"[0:a]atrim={start}:{section['start']}[a{i}];"
    start_and_ends.append([section['start'], section['end']])
    start = section['end']

base += f"[0:a]atrim={start}:{end}[a{len(deleted_sections)}];"

concat_base = ""
for i in range(len(deleted_sections) + 1):
    concat_base += f"[a{i}]"

base += concat_base
base += f"concat=n={len(deleted_sections) + 1}:a=1:v=0[outa]\""

base += " -map \"[outa]\" out.mp3"

with open("test.sh", "w") as f:
    f.write(base)
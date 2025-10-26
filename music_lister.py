import os
import re
import sys
import threading
import datetime
import time
from html5builder import HTML5Builder, HTML5Element

# USER PARAMETERS
# Set the folder to search
COMPOSITIONS_FOLDER="/mnt/c/Users/obrun/Music/Compositions"
#####

# Current script path
CURRENT_SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
DESIGN_FILE_PATH=os.path.join(CURRENT_SCRIPT_PATH, "design.css")
JS_FILE_PATH=os.path.join(CURRENT_SCRIPT_PATH, "sortfilter.js")

# Timeout and update frequency
UPDATE_FREQUENCY = 20
SOCKET_HOST = "localhost"
SOCKET_PORT = 5555

class Composition:
  """This class will hold the composition information.
  It will look for an info file on disk, based on the ALS file path given."""

  name = None
  artist = None
  album = None
  ep = None
  lyrics = None
  chords = None
  extra_info = None
  status = None
  rework = None

  als_file_path = None
  project_dir = None
  root_folder = None
  als_file_name = None
  audio_file = None
  last_activity = None

  def __init__(self, als_file_path, root_folder=None):
    self.als_file_path = als_file_path
    self.root_folder = root_folder
    self.project_dir = os.path.dirname(als_file_path)
    self.als_file_name = os.path.basename(als_file_path)
    modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(als_file_path))
    self.last_activity = modification_time.strftime("%Y-%m-%d %H:%M")
    self.audio_file = Helpers.get_audio_file_related_to_als(self.als_file_path)
    self.gather_composition_information()

  def gather_composition_information(self):
    info_file_path = Helpers.get_info_file_related_to_als(self.als_file_path)
    if info_file_path:
      info = Helpers.get_fields_from_file(info_file_path)
      self.name = info.get("name", self.als_file_name) or self.als_file_name
      self.artist = info.get("artist", None) or None
      self.album = info.get("album", None) or None
      self.ep = info.get("ep", None) or None
      self.lyrics = info.get("lyrics", None) or None
      self.extra_info = info.get("extra_info", None) or None
      self.chords = info.get("chords", None) or None
      self.status = info.get("status", None) or None
    self.make_proper_info()
  
  def make_proper_info(self):
    if self.status and Helpers.is_status_complete(self.status):
      self.status = "Finished"
      self.rework = None
    else:
      self.rework = self.status
      self.status = "In Progress"
  
  def is_finished(self):
    return self.status == "Finished"

  def __str__(self):
    return_string = f"# {self.artist+" - " if self.artist else ""}{self.name}\n"
    return_string += f"Last activity: {self.last_activity}"
    if self.album:
      return_string += f"-- Album: {self.album}"
    return_string += f" + Status: {self.status}\n"
    if self.rework:
      return_string += f" + Rework: {self.rework}\n"
    if self.chords:
      return_string += f" - Chords:\n"
      return_string += f"{self.chords}\n"
    if self.lyrics:
      return_string += f" - Lyrics:\n"
      return_string += f"{self.lyrics}\n"
    if self.extra_info:
      return_string += f" - Extra Info:\n"
      return_string += f"{self.extra_info}\n"
    return_string += f"{self.als_file_path}\n\n"
    audio_generated = "exported" if self.audio_file else "not exported"
    return_string += f" -> Audio file {audio_generated}"
    return return_string

  def __html__(self):
    tag = HTML5Builder()
    elem = HTML5Element

    list_of_elements = []

    # Song properties
    list_of_elements.append(tag.h2(self.name, cls="songname"))
    list_of_elements.append(tag.h3(f"Artist: {self.artist}", cls="artist"))
    if self.ep:
      list_of_elements.append(tag.h3(f"EP: {self.ep}", cls="album"))
    else:
      list_of_elements.append(tag.h3(f"Album: {self.album}", cls="album"))

    # Status
    list_of_elements.append(tag.p(f"Status: {self.status}", cls="status"))
    if not self.is_finished():
      rework_transform = Helpers.place_html_newlines(self.rework)
      rework_class = "rework"
      if rework_transform["multiple_lines"]:
        rework_class += " rework_multiple_lines"
      list_of_elements.append(tag.p(f"{str(tag.span("Rework: "))}{str(tag.span(rework_transform["html"]))}", cls=rework_class))

    # Last activity and path to project
    activity_path_elements = []
    #last activity
    last_activity = tag.p(f"Last modified: {str(tag.span(self.last_activity))}", cls="last_activity")
    activity_path_elements.append(last_activity)
    #als project file path
    path_to_display = self.als_file_path
    if self.root_folder:
      path_to_display = os.path.relpath(self.als_file_path,self.root_folder)
    file_path = tag.p(f"File path: {str(tag.span(path_to_display))}", cls="als_file_path")
    activity_path_elements.append(file_path)
    #audio file details
    audio_generated = tag.p(f"Sound file not exported", cls="audio_file not_exported")
    if self.audio_file:
      audio_generated = tag.p(f"<audio controls><source src='{Helpers.replace_wsl_disk_with_windows(self.audio_file)}' type='audio/wav'></audio>", cls="audio_file exported")
    activity_path_elements.append(audio_generated)
    activity_path_div = tag.div(activity_path_elements, cls="activity_path")
    list_of_elements.append(activity_path_div)

    # Extra details
    table_rows = [tag.tr([tag.th("Lyrics"), tag.td(Helpers.place_html_newlines(self.lyrics)["html"])]),
                  tag.tr([tag.th("Chords"), tag.td(Helpers.place_html_newlines(self.chords)["html"])])]
    if self.extra_info:
      table_row.append(tag.tr([tag.th("Extra"), tag.td(Helpers.place_html_newlines(self.extra_info)["html"])]))
    summary = tag.summary("More info")
    list_of_elements.append(tag.details([summary, tag.table(table_rows, border="0", cellpadding="5")]))
    
    # Assemble all elements
    composition_div_classes = "composition"
    data_status = ""
    if Helpers.is_status_complete(self.status):
      composition_div_classes += " finished"
      data_status = "finished"
    else:
      composition_div_classes += " unfinished"
      data_status = "unfinished"
    total_div = elem('div', list_of_elements,
                    {'class': composition_div_classes,
                     'data-activity': self.last_activity,
                     'data-status': data_status,
                     'data-title': self.name,
                     'data-album': self.album or self.ep or '',
                     'data-artist': self.artist or ''})

    return str(total_div)


class MusicLister:
  """This class will look for Ableton Live Sets.
  It will find them in the root_folder path."""

  root_folder = None
  output_html_file = None
  compositions = dict()

  def __init__(self, root_folder):
    assert os.path.isdir(root_folder)
    self.root_folder = root_folder
    self.output_html_file = os.path.join(root_folder, "index.html")
    self.look_for_als(root_folder)
  
  def look_for_als(self, path):
    if Helpers.is_als(path):
      self.compositions[path] = Composition(path, self.root_folder)
    
    if os.path.isfile(path):
      return

    als_present = Helpers.is_als_present_in_path(path)

    for element in os.listdir(path):
      next_path = os.path.join(path, element)
      if als_present and os.path.isdir(next_path):
        continue
      self.look_for_als(next_path)

  def export_html(self, silent=False):
    if not silent:
      print(f"Exporting HTML library to: {self.output_html_file}")
    file = open(self.output_html_file, 'w')
    file.write(self.__html__())
    file.close()
  
  def __str__(self):
    return_string = f"\n###################\nRoot folder: {self.root_folder}\n"
    return_string += f"Output HTML file: {self.output_html_file}\n"
    return_string += f"Number of compositions: {len(self.compositions)}\n"
    # return_string += "\n"
    # for name in self.compositions:
    #   return_string += f"{self.compositions[name]}"
    return_string += f"###################"
    return return_string

  def __html__(self):
    tag = HTML5Builder()
    elem = HTML5Element

    title = tag.title(f"Music Lister - {os.path.basename(self.root_folder)}")
    css = tag.link(href=Helpers.replace_wsl_disk_with_windows(DESIGN_FILE_PATH), rel="stylesheet")
    js = tag.script('', src=Helpers.replace_wsl_disk_with_windows(JS_FILE_PATH), type="text/javascript")
    meta = tag.meta(charset="UTF-8")
    head = tag.head([title, css, meta])

    main_title = tag.h1(title)

    # Details of music lister
    summary = tag.summary("About this list")
    detail1 = tag.li(f"Root folder: {tag.span(Helpers.replace_wsl_disk_with_windows(self.root_folder), cls="file_path")}")
    detail2 = tag.li(f"Output HTML file: {tag.span(Helpers.replace_wsl_disk_with_windows(self.output_html_file), cls="file_path")}")
    detail3 = tag.li(f"Number of compositions: {len(self.compositions)}")
    details_list = tag.ul([detail1, detail2, detail3])
    details = tag.div(tag.details([summary, details_list]), cls="lister_details")

    # Sort and filter options
    #sort
    # empty_sort = elem("option", ["---"], {'disabled':'', 'selected':''})
    activity_sort = tag.option("Last activity", value="activity")
    status_sort = tag.option("Status", value="status")
    title_sort = tag.option("Title", value="title")
    artist_sort = tag.option("Artist", value="artist")
    album_sort = tag.option("Album", value="album")
    sort_select = tag.select([activity_sort, status_sort, title_sort, artist_sort, album_sort], id="sortSelect")
    label_for_sort = elem("label", "Sort by: ", {"for": "sortSelect"})
    #filter
    input_finished = tag.input('', id='showFinished', type='checkbox')
    label_for_finished = elem("label", [input_finished, tag.span("Finished")], {})
    input_notfinished = tag.input('', id='showNotFinished', type='checkbox')
    label_for_notfinished = elem("label", [input_notfinished, tag.span("In Progress")], {})
    #assemble controls
    controls = tag.div([tag.div([label_for_sort, sort_select], cls="sort"),
                        tag.div(["Only show: ", label_for_finished, label_for_notfinished], cls="filter")],
                        cls="controls")

    # Compositions
    compositions = tag.div('', cls="compositions")
    for name in self.compositions:
      compositions.child.append(self.compositions[name].__html__())

    # Assemble it all together
    body = tag.body([main_title, details, controls, compositions, js])

    doc = tag.html([head, body], lang='html')
    return str(tag.doctype + str(doc))


class Helpers:
  """This helper class contains all basic functions as static."""

  @staticmethod
  def is_als(path):
    return os.path.isfile(path) and ".als" in path

  @staticmethod
  def is_infofile(path):
    return os.path.isfile(path) and ".info" in path

  @staticmethod
  def is_als_present_in_path(path):
    if os.path.isfile(path):
      return False
    for element in os.listdir(path):
      als_potential_path = os.path.join(path, element)
      if Helpers.is_als(als_potential_path):
        return True
    return False

  @staticmethod
  def get_info_file_related_to_als(path):
    file_path = path.replace(".als", ".txt")
    if os.path.isfile(file_path):
      return file_path
    return None

  @staticmethod
  def get_audio_file_related_to_als(path):
    file_path = path.replace(".als", ".wav")
    if os.path.isfile(file_path):
      return file_path
    return None

  @staticmethod
  def get_fields_from_file(path):
    fields = dict()

    # Function to save field
    def save_field(filed_name, field_value):
      if field_name and field_value:
        fields[field_name.strip()] = field_value.strip()

    with open(path) as file:
      field_name = None
      field_value = None
      for line in file:
        line = line.strip()
        try:
          key, value = line.split(':', 1)
          save_field(field_name, field_value)
          field_name = key
          field_value = value
        except:
          if field_name:
            field_value += f"\n{line}"
          pass
      save_field(field_name, field_value)
    return fields

  @staticmethod
  def is_status_complete(status):
    pattern = r'(?i)^(?:finished|complete|completed)$'
    match = re.findall(pattern, status.strip())
    if match:
      return True
    return False
  
  @staticmethod
  def replace_wsl_disk_with_windows(path):
    if os.path.isfile(path) or os.path.isdir(path):
      return re.sub(r'/mnt/([a-z]{1})', r'\1:', path)
    return None

  @staticmethod
  def place_html_newlines(text):
    tag = HTML5Builder
    return_dict = {"html": text, "multiple_lines": False}
    HTML_NEW_LINE = "<br/>"
    if return_dict["html"]:
      return_dict["html"] = return_dict["html"].strip().replace("\n", HTML_NEW_LINE)
      if HTML_NEW_LINE in return_dict["html"]:
        return_dict["multiple_lines"] = True
    return return_dict


# Main code
def main_code(silent=False):
  ml = MusicLister(COMPOSITIONS_FOLDER)
  ml.export_html(silent)

def main_thread(stop_event):
  while not stop_event.is_set():
    print("Scanning for compositions...")
    main_code(silent=True)
    time.sleep(UPDATE_FREQUENCY)

if __name__ == "__main__":
  if not (len(sys.argv) >= 1 and sys.argv[1] in ['once', 'periodically']):
    print("Usage:")
    print("  python music_lister.py once|periodically")
    print("  Options:")
    print("    once: Run the program once")
    print("    periodically: Run the program periodically in the background")
    sys.exit(2)

  print("Starting music_lister...")
  if sys.argv[1] == "once":
    main_code()
  elif sys.argv[1] == "periodically":
    stop_flag = threading.Event()    
    main_thread = threading.Thread(target=main_thread, args=(stop_flag,))
    print(f"Program running with update frequency of {UPDATE_FREQUENCY}s.")
    main_thread.start()
    try:
      # Main thread can stay idle or do other work.
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      print(f"\nStopping program… Please wait for completion (can take up to {UPDATE_FREQUENCY}s)…")
      stop_flag.set()
      main_thread.join()
    print("Program music_lister stopped.")

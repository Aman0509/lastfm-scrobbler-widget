from flask import Flask, jsonify, render_template
import requests, datetime

# Create Flask and Api object
app = Flask(__name__)


def fav_songs(user_loved_music_info):

    fav_song_list = []
    for i in user_loved_music_info['lovedtracks']['track']:
        fav_song_list.append(i['name'])

    return fav_song_list


@app.route('/username/<string:username>/<int:count>')
@app.route('/username/<string:username>/', defaults={'count': 1})
def get_data(username, count):

    lastfm_get_recent_track_api_url = f"https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={username}&api_key=5b6c4cae3423fd676a2ca2c250e8ad05&format=json"

    lastfm_loved_tracks_api_url = f"https://ws.audioscrobbler.com/2.0/?method=user.getLovedTracks&user={username}&api_key=5b6c4cae3423fd676a2ca2c250e8ad05&format=json"

    try:
        recent_track_response = requests.get(lastfm_get_recent_track_api_url)
        loved_response = requests.get(lastfm_loved_tracks_api_url)

        recent_track_response.raise_for_status()
        user_loved_music_info = loved_response.json()

        user_music_info = recent_track_response.json()
        uname = user_music_info['recenttracks']['@attr']['user']
        total_scrobble_count = user_music_info['recenttracks']['@attr']['total']

        user_fav_song_list = fav_songs(user_loved_music_info)

        user_data_list = []


        for i in range(count):

            song_info = {}
            song_info['song_name'] = user_music_info['recenttracks']['track'][i]['name']
            song_info['artist_name'] = user_music_info['recenttracks']['track'][i]['artist']['#text']
            song_info['album_image'] = user_music_info['recenttracks']['track'][i]['image'][0]['#text']

            if '@attr' in user_music_info.get('recenttracks').get('track')[i]:
                now_playing = True
                play_time = "scrobbling now"
            else:
                now_playing = False
                song_time = datetime.datetime.fromtimestamp(int(user_music_info['recenttracks']['track'][i]['date']['uts']))
                current_time_utc = datetime.datetime.now()
                play_time = str(current_time_utc - song_time).split(',')
                if len(play_time) == 1:
                    play_time = play_time[0].split(':')
                    if play_time[0] == '0':
                        play_time = play_time[1] + ' mins ago'
                    else:
                        play_time = play_time[0] + ' hr ago'
                elif len(play_time) > 1:
                    days = float(play_time[0].split()[0])
                    play_time = str(int(days * 0.00273973)) + ' yr ago'

            song_info['now_playing'] = now_playing
            song_info['play_time'] = play_time

            if song_info['song_name'] in user_fav_song_list:
                loved = True
            else:
                loved = False

            song_info['loved'] = loved
            user_data_list.append(song_info)

    except requests.exceptions.ConnectionError:
        return jsonify(error="no internet connection")
    except requests.exceptions.HTTPError:
        if recent_track_response.status_code == 404:
            return jsonify(message=f"user {username} not found")
        return jsonify(status_code=recent_track_response.status_code)

    return render_template("widget.html", uname=uname, total_scrobble_count=total_scrobble_count,user_data_list=user_data_list)


if __name__ == "__main__":
    app.run(debug=True)




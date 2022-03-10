$( document ).ready(async function() {
    track_info = await get_track_info_list();

    $("#download_songs_txt").click(() => {download_songs_txt(track_info)});
    $("#download_songs_csv").click(() => {download_songs_csv(track_info)});
});

/**
 *
 * @param {String} filename The name of the file - including its type
 * @param {String} file_content What should get written to the file
 */
function make_download_file(filename, file_content)
{
    const blob = new Blob([file_content], {
        type: "text/plain;charset=utf-8"
    });

    saveAs(blob, filename);
}

/**
 * @brief Creates a JSON mapping track_id to all of its info as given to the page
 * @returns {{
 *  id : {
 *    song_name : String
 *    artists : String
 *    album : String
 *  }
 * }}
 */
async function get_track_info_list()
{
    const overall_song_list_el = $("#song_list_display");
    // const song_list_el_list = overall_song_list_el.getElementsByTagName('div');
    const song_list_el_list = overall_song_list_el.children('div');

    let track_json = {};

    // reconstruct the song list using the div's for each track id
    await song_list_el_list.each(async (idx) => {
        let song_info_wrapper = song_list_el_list[idx];
        const track_id = song_info_wrapper.id;
        song_info_wrapper = $(`#${track_id}`)

        song_info = await get_song_artist_album_from_wrapper(song_info_wrapper);
        track_json[track_id] = song_info;
    });

    return track_json;
}

/**
 * @brief takes in a json of all the track info and puts it in a text format and saves it to a file.
 * @param {{
 *  id : {
 *   song_name : String
 *   artists : String
 *   album : String
 *  }
 * }} track_info_json
 */
function download_songs_txt(track_info_json)
{
    const playlist_name = $("#playlist_name").text();
    let file_content = "";

    // build up the string of file content using the given json
    for(const track_id in track_info_json)
    {
        const cur_track = track_info_json[track_id];

        // add the current line
        file_content += cur_track.song_name + " By ";
        file_content += cur_track.artists + " - ";
        file_content += cur_track.album + "\n";
    }

    let filename = playlist_name + ".txt";

    // // replace spaces with underscores
    filename = filename.replace(/\s/g, "_");

    make_download_file(filename, file_content);
}

function download_songs_json()
{
    const song_list_el = $("#song_list_display");
    const playlist_name = $("#playlist_name").text();

    // seperate by new lines - each song
    let song_list = song_list_el.text().split(/\r?\n/);
}


/**
 * @return {{
 *  song_name : String
 *  artists : String
 *  album : String
 * }}
 * @param {JQuerryElement} song_info_wrapper The element resulting from jqeury select that wraps all info for a song
 */
async function get_song_artist_album_from_wrapper(song_info_wrapper)
{
    const res = {
        "song_name": null,
        "artists": null,
        "album": null
    }


    const info_wrapper_kids = song_info_wrapper.children('div');

    // loop through kids of the wrapper to get artist, album, and song name
    await info_wrapper_kids.each((info_idx) => {
        const info_component_html_el = info_wrapper_kids[info_idx];
        const component_id = String(info_component_html_el.id);
        const info_component = $(`#${component_id}`)

        if(component_id.indexOf("song_name") >= 0 )
        {
            res.song_name = info_component.text();
        }
        else if (component_id.indexOf("artists") >= 0)
        {
            res.artists = info_component.text();
        }
        else if (component_id.indexOf("album") >= 0)
        {
            res.album = info_component.text();

        }
    });

    return res;

}

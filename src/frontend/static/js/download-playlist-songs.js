$( document ).ready(function() {
    $("#download_songs_txt").click(download_songs_txt);
    $("#download_songs_csv").click(download_songs_json);
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

function download_songs_txt()
{
    const song_list_el = $("#song_list_display");
    const playlist_name = $("#playlist_name").text();

    // seperate by new lines - each song
    let song_list = song_list_el.text().split(/\r?\n/);

    // remove empty space songs
    song_list = song_list.filter(function(word) { return word.trim() != ''; })

    // remove any weird white space artifacts from jinja
    const final_song_list = song_list.map(song => song.trim());

    const file_content = final_song_list.join('\n');
    let filename = playlist_name + ".txt";

    // replace spaces with underscores
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

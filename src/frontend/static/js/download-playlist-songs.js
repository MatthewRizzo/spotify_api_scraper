$( document ).ready(function() {
    // document.getElementById("download_songs_txt").addEventListener("click", download_songs);
    $("#download_songs_txt").click(download_songs);
});


function download_songs()
{
    console.log("button press registered");
    const song_list_el = $("#song_list_display");

    // seperate by new lines - each song
    let song_list = song_list_el.text().split(/\r?\n/);

    // remove empty space songs
    song_list = song_list.filter(function(word) { return word.trim() != ''; })

    // songs have "        " - artifact of jinja format. remove that
    const final_song_list = song_list.map(song => song.trim());
    console.log(`song_list = `)
    for(const song of final_song_list)
    {
        console.log(song)
    }
}

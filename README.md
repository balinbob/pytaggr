# pytaggr

<h5>A command-line tool for tagging and editing tags in audio formats which can also<br>
tag from filenames/paths, and rename files from tags. It implements the Mutagen<br>
pure-python library for working with audio metadata, which adheres to the principles<br>
of standardized tagging.  It can also write multiple values for a tag (such as genre, or artist).</h5>

<h5>Using globs (*.flac, ~/Music/Album004/0?\ -\ *.mp3), batch editing of multiple files can<br>
be done.  PyTaggr is well-suited for editing tracks in the files of an album, set, etc.</h5>

<h5>Like many cli utilities, with a bit of practice it can become a powerful tool for working<br>
with flac, apev2, ogg vorbis, & mp3 files.</h5>

Usage: pytaggr [options] filenames

*  Options:<br> 
*  -h|--help<br>
	*    show this help text & exit<br>
*  -t|--tag TAG=VALUE<br>
	*    set a tag, ie pytaggr -t artist='The Beatles' -t album='Rubber Soul' *.flac<br>
*  -a|--add TAG=VALUE<br>
	*    set or add a value to a tag, without removing any existing values<br>
*  -r|--remove TAG *or* TAG=VALUE<br>
	*    remove a tag *or* a value from a multi-valued tag<br>
*  -p PATTERN|--pattern=PATTERN<br>
	*    substitution pattern from filepath/name, ie: pytaggr -p '%l/%n - %t.flac' *.flac<br>
*  --fn2tag PATTERN<br>
	*    same as -p|--pattern<br>
*  --tag2fn PATTERN<br>
	*    substitution pattern from existing tags, to rename files, ie: pytaggr '%n. %t' *.mp3<br>
*  -j|--justify<br>
	*    zero-justify tracknumbers ie 01 rather that 1<br>
*  --clear<br>
	*    clear all tags<br>
*  -n|--noact<br>
	*    only show the changes that would be made<br>
*  -c|--confirm<br>
	*    show changes and prompt for confirmation<br>
*  -q|--quiet<br>
	*    resist printing on stdout<br>
*  -m '/ -' | --map '/ -'<br>
	*    tricky one, used in conjunction with --tag2fn, convert any of one char to another char<br>
	*    (similar to the tr utility)<br>
	*    useful for weeding out non-filename-friendly chars<br>
*  -i|--index<br>
	*    index-tag the files in the order they currently sort by filename<br>
	*    places an integer tag into the file, in case sort order gets botched
	*    (such as accidentally removing leading tracknumbers from filenames)<br>

Using no options (only a filename) prints all tags in the file

pytaggr id3help: for help with id3 tags


*	examples:<br>
*       pytaggr -t artist="Jerry Garcia Band" --fn2tag '%n %t.flac' *.flac<br>
	*	tags all flac files with an artist, and gets the tracknumber & title from the filename

*	pytaggr --tag2fn '~/Music/%a/%l/%n - %t.mp3' 1*.mp3<br>
	*  	renames all mp3 files which begin with '1' this way:<br>
	*	~/Music/Artist Name/Album Title/Number - Title.mp3<br>
	*	(provided the files are properly tagged)






/**
 * Removes the '#' symbol in front of a color specification
 *
 * E.g.: "#fff" -> "fff"
 *       "#ffffff" -> "ffffff"
 *       "ffffff" -> "ffffff"
 */
function util_hex_color(color) {
    if (color.substring(0,1) == "#") {
	return color.substring(1, color.length);
    }
    return color;
}


function includes(arr,obj) {
    return (arr.indexOf(obj) != -1);
}




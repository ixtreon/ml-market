
/* 
Creates a static "price bar" in the provided SVG parent element for the specified outcomes. 
The price bar visualises the outcomes and their current (instantaneous) prices. 

The outcomes must be an array of tuples (outcome_name, outcome_price). Each tuple is in turn a 2-el array. 

TODO: support update instead of just create
*/
function price_bar(el, outs) {
    // http://stackoverflow.com/questions/16488884/add-svg-element-to-existing-svg-using-dom
    var wSum = 0    // the width-sum of the elements so far
    var bar_colors = [
        'lightskyblue',
        'lightpink',
        'lightgreen',
        'lightsalmon',
        'lightyellow',
    ];
    for (i = 0; i < outs.length; i++) {
        var bar = document.createElementNS("http://www.w3.org/2000/svg", 'rect'); //Create a path in SVG's namespace
        var txt = document.createElementNS("http://www.w3.org/2000/svg", 'text'); //Create a path in SVG's namespace

        var price = outs[i][1]
        var desc = outs[i][0]

        bar.setAttribute("width", price + "%")
        bar.setAttribute("height", "100%")
        bar.setAttribute("x", wSum + "%")
        bar.style.fill = bar_colors[i % bar_colors.length];
        bar.setAttribute("title", desc + ": 0." + price)

        //txt.setAttribute("width", price + "")
        //txt.setAttribute("height", "100")
        txt.setAttribute("x", wSum + "%")
        txt.setAttribute("y", 0)
        txt.setAttribute("fill", "black")
        txt.setAttribute("font-family", "Verdana")
        txt.setAttribute("font-size", "20")
        //txt.style.fill = fill[i % fill.length];
        txt.appendChild(document.createTextNode("kurvo"))


        wSum += price
        el.appendChild(bar)
        //el.appendChild(txt)

    }
}
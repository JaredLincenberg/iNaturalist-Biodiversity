function toggleMap(record, observer){
    // debugger
    // console.log(record.dataset.bsTheme)
    console.log(observer)
    var graphDiv = document.getElementById('bdMap')

    var updateLight = {
        'map.style' : 'carto-positron',
        'paper_bgcolor' : '#FFF',
        'font.color' : '#000'
        
    }
    var updateDark = {
        'map.style' : 'carto-darkmatter',
        'paper_bgcolor' : '#222',
        'font.color' : '#0d49f1',
    }
    const newTheme = record[0].target.dataset.bsTheme
    if (newTheme === "dark"){

        Plotly.relayout(graphDiv, updateDark)
    } else if (newTheme==="light"){
        Plotly.relayout(graphDiv, updateLight)
    }
}
const observer = new MutationObserver(toggleMap)
observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-bs-theme']
});
// console.log("test")


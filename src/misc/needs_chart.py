# Helper function that determines if we need to make an /charts/id request
def needs_chart(form):
    return (form.maxNotes.data or form.minNotes.data 
        or form.difficultyClass.data or form.excludeDoubles.data 
        or form.shockNotes.data != "Include shock charts" )
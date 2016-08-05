[files]
# TODO: Instantiate dir
dir = /path/to/dataset
img = %(dir)s/stack1-image.h5
      %(dir)s/stack2-image.h5
      %(dir)s/stack3-image.h5
      %(dir)s/stack4-image.h5
      %(dir)s/stack5-image.h5
      %(dir)s/stack6-image.h5
      %(dir)s/stack7-image.h5
      %(dir)s/stack8-image.h5
      %(dir)s/stack9-image.h5
      %(dir)s/stack10-image.h5
lbl = %(dir)s/stack1-label.h5
      %(dir)s/stack2-label.h5
      %(dir)s/stack3-label.h5
      %(dir)s/stack4-label.h5
      %(dir)s/stack5-label.h5
      %(dir)s/stack6-label.h5
      %(dir)s/stack7-label.h5
      %(dir)s/stack8-label.h5
      %(dir)s/stack9-label.h5
      %(dir)s/stack10-label.h5

[image]
file = img
preprocess = {'type':'standardize','mode':'2D'}

[label]
file = lbl
transform = {'type':'affinitize'}

[dataset]
input = image
label = label

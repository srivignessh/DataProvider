[files]
dir = ../dataset/zfish
img = %(dir)s/r1.daan.img.h5
      %(dir)s/r1.kyle.img.h5
      %(dir)s/r1.merlin.1.img.h5
      %(dir)s/r2.kyle.img.h5
      %(dir)s/r2.merlin.img.h5
      %(dir)s/r2.selden.img.h5
      %(dir)s/r1.merlin.2.img.h5
lbl = %(dir)s/r1.daan.lbl.h5
      %(dir)s/r1.kyle.lbl.h5
      %(dir)s/r1.merlin.1.lbl.h5
      %(dir)s/r2.kyle.lbl.h5
      %(dir)s/r2.merlin.lbl.h5
      %(dir)s/r2.selden.lbl.h5
      %(dir)s/r1.merlin.2.lbl.h5

[image]
file = img
preprocess = {'type':'standardize','mode':'2D'}

[label]
file = lbl
transform = {'type':'affinitize'}

[dataset]
input = image
label = label
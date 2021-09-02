
import arcpy
from arcpy import env

# Please change these variable according to your environment
in_fc = "random_points"
out_fc = "polygon"          # This is your final output
env.workspace = "C:/Users/Umesh/Documents/ArcGIS/Scratch"



sr = arcpy.Describe(in_fc).spatialReference

# Add polygon index field
poly = arcpy.CreateFeatureclass_management(env.workspace, out_fc, "POLYGON", "","","",sr)
poly_fl = arcpy.MakeFeatureLayer_management(poly,"polygon_layer")
arcpy.AddField_management(poly_fl,"poly_index","LONG")

# Adding Field
arcpy.AddField_management(in_fc,"value_sum","LONG")
arcpy.AddField_management(in_fc,"poly_index","LONG")

# Getting values from each point feature and adding them to the new field
uc = arcpy.da.UpdateCursor(in_fc, ["value", "value_sum", "poly_index"])
sum = 0
poly_index = set() # Create an empty set to store (future) polygon_ids

for row in uc:
    sum += row[0]
    poly_id = int(sum/1000+1)
    poly_index.add(poly_id)
    uc.updateRow([row[0], sum, poly_id ])

del sum
del uc

# Now preparation is done

# Iterating through polygon index list
for i in poly_index:
    x_list = []
    y_list = []
    sc = arcpy.da.SearchCursor(in_fc, ["SHAPE@X", "SHAPE@Y"],"{} = {}".format(arcpy.AddFieldDelimiters(env.workspace, "poly_index"), i))
    for row in sc:
        # Add x and y coordinates into seperate list
        x_list.append(row[0])
        y_list.append(row[1])
    del row
    del sc
    max_x = max(x_list)
    max_y = max(y_list)
    min_x = min(x_list)
    min_y = min(y_list)

    p1 = arcpy.Point(min_x, min_y)
    p2 = arcpy.Point(min_x, max_y)
    p3 = arcpy.Point(max_x, max_y)
    p4 = arcpy.Point(max_x, min_y)

    # Creating a polygon geometry and inserting into the output fc
    poly = arcpy.Polygon(arcpy.Array([p1,p2,p3,p4]))
    ic = arcpy.da.InsertCursor(poly_fl, ["SHAPE@", "poly_index"])
    ic.insertRow([poly, i])
    del poly
    del ic
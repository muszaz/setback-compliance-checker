import arcpy

arcpy.env.overwriteOutput = True

sites_input = arcpy.GetParameterAsText(0)
boundary = arcpy.GetParameterAsText(1)
watercourses_input = arcpy.GetParameterAsText(2)
wetlands_input = arcpy.GetParameterAsText(3)
setback_distance = arcpy.GetParameterAsText(4)
output_table = arcpy.GetParameterAsText(5)

arcpy.analysis.Clip(watercourses_input, boundary, "watercourses_toronto")
arcpy.analysis.Clip(wetlands_input, boundary, "wetlands_toronto")
arcpy.analysis.Clip(sites_input, boundary, "proposed_sites_toronto")

arcpy.analysis.Buffer("watercourses_toronto", "watercourses_buffer_to", setback_distance, dissolve_option="ALL")
arcpy.analysis.Buffer("wetlands_toronto", "wetlands_buffer_to", setback_distance, dissolve_option="ALL")

arcpy.management.AddField("proposed_sites_toronto", "Watercourse_Viol", "TEXT", field_length=5)
arcpy.management.AddField("proposed_sites_toronto", "Wetland_Viol", "TEXT", field_length=5)
arcpy.management.AddField("proposed_sites_toronto", "Overall_Status", "TEXT", field_length=10)
arcpy.management.AddField("proposed_sites_toronto", "Violation_Type", "TEXT", field_length=15)

arcpy.management.CalculateField("proposed_sites_toronto", "Watercourse_Viol", "'NO'", "PYTHON3")
arcpy.management.CalculateField("proposed_sites_toronto", "Wetland_Viol", "'NO'", "PYTHON3")
arcpy.management.CalculateField("proposed_sites_toronto", "Overall_Status", "'PASS'", "PYTHON3")

arcpy.management.SelectLayerByLocation("proposed_sites_toronto", "INTERSECT", "watercourses_buffer_to")
with arcpy.da.UpdateCursor("proposed_sites_toronto", ["Watercourse_Viol", "Overall_Status"]) as cursor:
    for row in cursor:
        row[0] = "YES"
        row[1] = "FAIL"
        cursor.updateRow(row)
arcpy.management.SelectLayerByAttribute("proposed_sites_toronto", "CLEAR_SELECTION")

arcpy.management.SelectLayerByLocation("proposed_sites_toronto", "INTERSECT", "wetlands_buffer_to")
with arcpy.da.UpdateCursor("proposed_sites_toronto", ["Wetland_Viol", "Overall_Status"]) as cursor:
    for row in cursor:
        row[0] = "YES"
        row[1] = "FAIL"
        cursor.updateRow(row)
arcpy.management.SelectLayerByAttribute("proposed_sites_toronto", "CLEAR_SELECTION")

with arcpy.da.UpdateCursor("proposed_sites_toronto", ["Watercourse_Viol", "Wetland_Viol", "Violation_Type"]) as cursor:
    for row in cursor:
        wc, wl = row[0], row[1]
        if wc == "YES" and wl == "YES":
            row[2] = "Both"
        elif wc == "YES":
            row[2] = "Watercourse"
        elif wl == "YES":
            row[2] = "Wetland"
        else:
            row[2] = "None"
        cursor.updateRow(row)

arcpy.conversion.ExportTable("proposed_sites_toronto", output_table)

arcpy.management.SelectLayerByAttribute("proposed_sites_toronto", "NEW_SELECTION", "Watercourse_Viol = 'YES'")
print("Watercourse violations:", arcpy.management.GetCount("proposed_sites_toronto")[0])

arcpy.management.SelectLayerByAttribute("proposed_sites_toronto", "NEW_SELECTION", "Wetland_Viol = 'YES'")
print("Wetland violations:", arcpy.management.GetCount("proposed_sites_toronto")[0])

arcpy.management.SelectLayerByAttribute("proposed_sites_toronto", "CLEAR_SELECTION")
print("Done.")





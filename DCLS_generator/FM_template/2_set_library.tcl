puts ""
puts ""
puts "INFO : Set library"
puts ""
puts ""

if { ![info exists ::env(DK_HOME)] || $::env(DK_HOME) == "" } {
    puts "ERROR: DK_HOME is not defined. Exiting."
    puts "INFO : Please source SourceMe.csh in N1 working repository"
    quit
}

set DK_HOME [getenv DK_HOME]
if {![info exist DK_HOME] || $DK_HOME == "" } {
    puts "ERROR: DK_HOME is not defined. Exiting."
    puts "INFO : Please check SourceMe.csh in N1 working repository"
    quit
}

set LIBRARY_DIR [list]
set TARGET_LIBRARY_FILES [list]

source ${DK_HOME}/lib_tcl/set_library_std.tcl
source ${DK_HOME}/lib_tcl/set_library_imem_arm_v2.tcl

puts ""
puts ""
puts "INFO :PrintLIBRARY_DIR and TARGET_LIBRARY_FILES"
puts ""
puts ""
puts "print LIBRARY_DIR"
foreach item $LIBRARY_DIR {
    puts $item
}

puts ""
puts ""
puts "print TARGET_LIBRARY_FILES"
foreach item $TARGET_LIBRARY_FILES {
    puts $item
}
puts ""
puts ""

set symbol_library      ""
set synthetic_library   ""
set link_library        "$TARGET_LIBRARY_FILES"

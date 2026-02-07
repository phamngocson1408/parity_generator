
puts ""
puts ""
puts "Set environment variable"
puts ""
puts ""
if { ![info exists ::env(N1_ASIC_HOME)] || $::env(N1_ASIC_HOME) == "" } {
    puts "ERROR: N1_ASIC_HOME is not defined. Exiting."
    puts "INFO : Please source SourceMe.csh in N1 working repository"
    quit
}

# Set all variables from environment variables
foreach name [array names env] {
    set "$name" "$env($name)"
}

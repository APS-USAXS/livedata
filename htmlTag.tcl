#!/usr/bin/tclsh
#
# htmlTag.tcl

#####################################################################

proc makeTagHTML {fullTag {content {}} {indent 1}} {
  #
  # This is the new version of how to make HTML tags
  #
  set parts [split $fullTag " "]
  set shortTag [lindex $parts 0]
  set tag "<$fullTag>"
  if [string length $content] {
    if {$indent} {
      append tag "\n"
      set indentation "  "
      foreach line [split $content "\n"] {
        # indent each line of the content
        if [string length $line] {
          # puts [format "%5d: <%s>\n" [string length $line] $line]
          append tag "$indentation$line\n"
        }
      }
    } else {
      append tag "$content"
    }
    append tag "</$shortTag>"
  }
  return "$tag\n"
}

#####################################################################

proc htmlTag args {
  #
  # This is the old version of how to make HTML tags
  #
  if ![llength $args] {
    error {usage: htmlTag tag [content [indent [options]]]}
    return
  }
  set content ""
  set indent 0
  set options ""
  set tag [lindex $args 0]
  if {[llength $args] > 1} {set content [lindex $args 1]}
  if {[llength $args] > 2} {set indent  [lindex $args 2]}
  if {[llength $args] > 3} {set options [lindex $args 3]}
  
  set out "<$tag"
  if [string length [string trim $options]] {
    append out " $options"
  }
  append out >
  if [string length [string trim $content]] {
    if $indent {
      append out \n
      foreach line [split $content \r\n] {
    	append out "  $line\n"
      }
    } else {
      append out $content
    }
    append out </$tag>
  }
  return $out
}

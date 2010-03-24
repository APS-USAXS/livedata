
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

proc setStatus message {
  global tool
  set tool(status) $message
  update idletasks
}

proc unknownSpecFileSection part {
  setStatus "Notice: unknown spec file section:  $part"
  #error "Notice: unknown spec file section:  $part"
  # textWindow \
  #   "unknown spec file section" \
  #   "Notice: unknown spec file section" \
  #   $part
}

proc readFile file {
  if {[file exists $file]} {
    set f [open $file r]
    set buffer [read $f]
    close $f
    return $buffer
  }
}

proc readSpecFile file {
  global specData tool
  if {![file exists $file]} return

  set tool(specFile) $file
  set tool(path) [file dirname $file]
  set tool(file) [lindex [file split $file] end]

  catch {unset specData}
  set specData(fileName) $file
  setStatus "loading file $file"
  set specData(rawFileContents) [readFile $file]
  #
  # >>>>>>>>>>>>>> look here for spec file format
  #
  # split the various scans from the file contents into a Tcl list
  setStatus "separating scans in $file"
  set searchText  "\n\n#"
  set replaceText "\} \{#"
  regsub -all $searchText $specData(rawFileContents) $replaceText buf
  # look through each part of the spec file
  foreach part \{$buf\} {
    switch -- [string index $part 1] {
      E - F {
        set specData(fileHeader) $part
        setStatus "File header"
      }
      S {
        scan $part %*s%s scanNumber
        update idletasks
        # make certain we can still identify this particular data
        # even if this spec file has more than one
        # instance of the same scan number
        set scanID S$scanNumber
        if [info exists specData($scanID)] {
          for {set i 1} {1} {incr i} {
            set scanID [format S%s_%s $scanNumber $i]
            if {![info exists specData($scanID)]} break
          }
        }
        lappend specData(scanList) $scanID
        #lappend tool(status) $scanID
        #update idletasks
        setStatus "read scan $scanID"
        set specData($scanID) $part
        set specData($scanID,line1)  [lindex [split $part \n] 0]
        # only interpret the scan the first time 
        # it has been selected from the list
        #interpretScanID $scanID
      }
      default {
        #
        # trap the situation when [string length $part] is too big
        #
        unknownSpecFileSection $part
        #tk_messageBox \
        #  -default ok \
        #  -icon info \
        #  -message "Notice: unknown spec file section\n$part" \
        #  -title "unknown spec file section" \
        #  -type ok
      }
    }
  }
  if ![info exists specData(fileHeader)] {
    # it is possible to create a file where the #F is missing
    # recover gracefully from this
    set specData(fileHeader) [lindex \{$buf\} 0]
    setStatus "incomplete file header recovered"
  }
  setStatus "Read spec data file: $file"
}

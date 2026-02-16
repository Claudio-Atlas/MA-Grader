' Topic 1 DQ 1 - Auto Checker with AI Feedback
' Add this module to the DQ Excel file or your personal macro workbook
' Requires: Reference to "Microsoft XML, v6.0" (Tools > References)

Option Explicit

' ============================================
' CONFIGURATION - Set your API key here
' ============================================
Private Const OPENAI_API_KEY As String = "YOUR_API_KEY_HERE"
Private Const MODEL As String = "gpt-4o-mini"

' ============================================
' MAIN ENTRY POINT - Run this macro
' ============================================
Public Sub CheckDQ1AndGenerateFeedback()
    Dim ws As Worksheet
    Dim errors As Collection
    Dim errorText As String
    Dim feedback As String
    Dim studentName As String
    
    On Error GoTo ErrorHandler
    
    ' Get the Basic Excel Formulas sheet
    Set ws = ThisWorkbook.Worksheets("Basic Excel Formulas")
    
    ' Get student name
    studentName = Trim(CStr(ws.Range("H2").Value))
    If studentName = "" Or studentName = "Your Name Here" Then
        studentName = "Student"
    End If
    
    ' Collect all errors
    Set errors = New Collection
    
    ' Check inputs (a and b)
    CheckInputCells ws, errors
    
    ' Check basic operation formulas (F8:F12)
    CheckBasicFormulas ws, errors
    
    ' Check basic formula formatting (2 decimals)
    CheckBasicFormatting ws, errors
    
    ' Check range data exists
    CheckRangeData ws, errors
    
    ' Check range formulas (H20:H22)
    CheckRangeFormulas ws, errors
    
    ' Check range formatting
    CheckRangeFormatting ws, errors
    
    ' Build error summary
    If errors.Count = 0 Then
        MsgBox "✓ No corrections needed! This submission looks good.", vbInformation, "DQ1 Checker"
        Exit Sub
    End If
    
    errorText = BuildErrorText(errors)
    
    ' Show what was found
    Debug.Print "=== Errors Found ===" & vbCrLf & errorText
    
    ' Call API for feedback
    feedback = GenerateAIFeedback(studentName, errorText)
    
    ' Show feedback and copy to clipboard
    ShowAndCopyFeedback studentName, feedback
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description, vbCritical, "DQ1 Checker Error"
End Sub

' ============================================
' CHECK FUNCTIONS
' ============================================

Private Sub CheckInputCells(ws As Worksheet, errors As Collection)
    Dim cellA As Range, cellB As Range
    Set cellA = ws.Range("B8")
    Set cellB = ws.Range("C8")
    
    ' Check if inputs exist and are numeric
    If IsEmpty(cellA.Value) Then
        errors.Add "Cell B8 (input 'a'): No value entered"
    ElseIf Not IsNumeric(cellA.Value) Then
        errors.Add "Cell B8 (input 'a'): Should be a number, found '" & cellA.Value & "'"
    End If
    
    If IsEmpty(cellB.Value) Then
        errors.Add "Cell C8 (input 'b'): No value entered"
    ElseIf Not IsNumeric(cellB.Value) Then
        errors.Add "Cell C8 (input 'b'): Should be a number, found '" & cellB.Value & "'"
    End If
End Sub

Private Sub CheckBasicFormulas(ws As Worksheet, errors As Collection)
    Dim i As Integer
    Dim cell As Range
    Dim formula As String
    Dim operations As Variant
    Dim expectedPatterns As Variant
    
    ' F8=addition, F9=subtraction, F10=multiplication, F11=division, F12=exponentiation
    operations = Array("addition (a+b)", "subtraction (a-b)", "multiplication (a*b)", "division (a/b)", "exponentiation (a^b)")
    expectedPatterns = Array("+", "-", "*", "/", "^")
    
    For i = 0 To 4
        Set cell = ws.Range("F" & (8 + i))
        
        If IsEmpty(cell.Value) Then
            errors.Add "Cell F" & (8 + i) & " (" & operations(i) & "): Empty - needs a formula"
        ElseIf Not cell.HasFormula Then
            errors.Add "Cell F" & (8 + i) & " (" & operations(i) & "): Hardcoded value '" & cell.Value & "' - should be a formula using cell references"
        Else
            formula = cell.formula
            ' Check if formula contains the right operator
            If InStr(formula, expectedPatterns(i)) = 0 Then
                errors.Add "Cell F" & (8 + i) & " (" & operations(i) & "): Formula '" & formula & "' doesn't appear to use the " & expectedPatterns(i) & " operator"
            End If
            ' Check if formula references B8 and C8
            If InStr(UCase(formula), "B8") = 0 Or InStr(UCase(formula), "C8") = 0 Then
                errors.Add "Cell F" & (8 + i) & " (" & operations(i) & "): Formula should reference cells B8 and C8 (the input values)"
            End If
        End If
    Next i
End Sub

Private Sub CheckBasicFormatting(ws As Worksheet, errors As Collection)
    Dim i As Integer
    Dim cell As Range
    Dim numFormat As String
    
    For i = 8 To 12
        Set cell = ws.Range("F" & i)
        If Not IsEmpty(cell.Value) And IsNumeric(cell.Value) Then
            numFormat = cell.NumberFormat
            ' Check for 2 decimal places (common formats: "0.00", "#,##0.00", etc.)
            If InStr(numFormat, ".00") = 0 And InStr(numFormat, ".??") = 0 Then
                If numFormat = "General" Or Right(numFormat, 2) <> "00" Then
                    errors.Add "Cell F" & i & ": Should be formatted to show 2 decimal places"
                End If
            End If
        End If
    Next i
End Sub

Private Sub CheckRangeData(ws As Worksheet, errors As Collection)
    Dim i As Integer
    Dim cell As Range
    Dim hasData As Boolean
    
    hasData = False
    For i = 20 To 27
        Set cell = ws.Range("E" & i)
        If Not IsEmpty(cell.Value) And IsNumeric(cell.Value) Then
            hasData = True
            Exit For
        End If
    Next i
    
    If Not hasData Then
        errors.Add "Data range E20:E27: No numeric data entered - need values for the range operations"
    End If
End Sub

Private Sub CheckRangeFormulas(ws As Worksheet, errors As Collection)
    Dim cell As Range
    Dim formula As String
    Dim funcNames As Variant
    Dim rowNums As Variant
    Dim i As Integer
    
    funcNames = Array("AVERAGE", "SUM", "PRODUCT")
    rowNums = Array(20, 21, 22)
    
    For i = 0 To 2
        Set cell = ws.Range("H" & rowNums(i))
        
        If IsEmpty(cell.Value) Then
            errors.Add "Cell H" & rowNums(i) & " (" & funcNames(i) & "): Empty - needs a formula"
        ElseIf Not cell.HasFormula Then
            errors.Add "Cell H" & rowNums(i) & " (" & funcNames(i) & "): Hardcoded value '" & cell.Value & "' - should be a formula"
        Else
            formula = UCase(cell.formula)
            ' Check for correct function
            If InStr(formula, funcNames(i)) = 0 Then
                errors.Add "Cell H" & rowNums(i) & ": Should use the " & funcNames(i) & " function"
            End If
            ' Check for proper range (should use colon, not comma for individual cells)
            If InStr(formula, "E20:E27") = 0 And InStr(formula, "E20:e27") = 0 Then
                ' Check for common mistakes
                If InStr(formula, ",") > 0 And InStr(formula, ":") = 0 Then
                    errors.Add "Cell H" & rowNums(i) & ": Use a range with colon (E20:E27) instead of listing individual cells with commas"
                ElseIf InStr(formula, "E20") = 0 Or InStr(formula, "E27") = 0 Then
                    errors.Add "Cell H" & rowNums(i) & ": Range should be E20:E27 (check your range references)"
                End If
            End If
        End If
    Next i
End Sub

Private Sub CheckRangeFormatting(ws As Worksheet, errors As Collection)
    Dim cell As Range
    Dim numFormat As String
    
    ' H20 = 2 decimals
    Set cell = ws.Range("H20")
    If Not IsEmpty(cell.Value) And IsNumeric(cell.Value) Then
        numFormat = cell.NumberFormat
        If InStr(numFormat, ".00") = 0 And numFormat = "General" Then
            errors.Add "Cell H20 (Average): Should be formatted to 2 decimal places"
        End If
    End If
    
    ' H21 = 1 decimal
    Set cell = ws.Range("H21")
    If Not IsEmpty(cell.Value) And IsNumeric(cell.Value) Then
        numFormat = cell.NumberFormat
        If InStr(numFormat, ".0") = 0 And numFormat = "General" Then
            errors.Add "Cell H21 (Sum): Should be formatted to 1 decimal place"
        End If
    End If
    
    ' H22 = 3 decimals
    Set cell = ws.Range("H22")
    If Not IsEmpty(cell.Value) And IsNumeric(cell.Value) Then
        numFormat = cell.NumberFormat
        If InStr(numFormat, ".000") = 0 And numFormat = "General" Then
            errors.Add "Cell H22 (Product): Should be formatted to 3 decimal places"
        End If
    End If
End Sub

' ============================================
' HELPER FUNCTIONS
' ============================================

Private Function BuildErrorText(errors As Collection) As String
    Dim result As String
    Dim i As Integer
    
    result = ""
    For i = 1 To errors.Count
        result = result & "- " & errors(i) & vbCrLf
    Next i
    
    BuildErrorText = result
End Function

' ============================================
' AI FEEDBACK GENERATION
' ============================================

Private Function GenerateAIFeedback(studentName As String, errorText As String) As String
    Dim http As Object
    Dim url As String
    Dim requestBody As String
    Dim response As String
    Dim jsonStart As Long, jsonEnd As Long
    
    ' Check API key
    If OPENAI_API_KEY = "YOUR_API_KEY_HERE" Or OPENAI_API_KEY = "" Then
        GenerateAIFeedback = "API key not configured. Errors found:" & vbCrLf & vbCrLf & errorText
        Exit Function
    End If
    
    url = "https://api.openai.com/v1/chat/completions"
    
    ' Build the prompt
    Dim systemPrompt As String
    Dim userPrompt As String
    
    systemPrompt = "You are Professor Clayton Ragsdale, a supportive online math instructor at GCU. " & _
                   "Write DQ feedback that is warm but direct. Your style:" & vbCrLf & _
                   "- Start with 'Hi [FirstName],' (friendly, not formal)" & vbCrLf & _
                   "- Be encouraging but clear about exactly what needs fixing" & vbCrLf & _
                   "- Give specific cell references and what the correct approach is" & vbCrLf & _
                   "- Keep it concise - students skim, so bullet points are good for multiple issues" & vbCrLf & _
                   "- End with: let them know if they resubmit with corrections, you can regrade and it will count as a substantive post" & vbCrLf & _
                   "- Sign off with just 'Professor Ragsdale' (no email, keep it short)" & vbCrLf & _
                   "- Tone: helpful teacher, not robotic grader. You want them to learn." & vbCrLf & _
                   "- Do NOT use emojis in DQ feedback (save those for announcements)" & vbCrLf & _
                   "- Keep total response under 150 words unless many errors"
    
    userPrompt = "Student: " & studentName & vbCrLf & vbCrLf & _
                 "Assignment: Topic 1 DQ 1 (Basic Excel Formulas)" & vbCrLf & vbCrLf & _
                 "Errors found:" & vbCrLf & errorText & vbCrLf & _
                 "Write the feedback response I'll paste into the LMS."
    
    ' Escape for JSON
    systemPrompt = EscapeJSON(systemPrompt)
    userPrompt = EscapeJSON(userPrompt)
    
    requestBody = "{""model"":""" & MODEL & """," & _
                  """messages"":[" & _
                  "{""role"":""system"",""content"":""" & systemPrompt & """}," & _
                  "{""role"":""user"",""content"":""" & userPrompt & """}" & _
                  "],""max_tokens"":500,""temperature"":0.7}"
    
    ' Make the request
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Authorization", "Bearer " & OPENAI_API_KEY
    http.send requestBody
    
    If http.Status = 200 Then
        response = http.responseText
        ' Extract content from JSON response
        GenerateAIFeedback = ExtractContent(response)
    Else
        GenerateAIFeedback = "API Error (" & http.Status & "): " & http.responseText & vbCrLf & vbCrLf & _
                            "Errors found:" & vbCrLf & errorText
    End If
    
    Set http = Nothing
End Function

Private Function EscapeJSON(text As String) As String
    Dim result As String
    result = text
    result = Replace(result, "\", "\\")
    result = Replace(result, """", "\""")
    result = Replace(result, vbCrLf, "\n")
    result = Replace(result, vbCr, "\n")
    result = Replace(result, vbLf, "\n")
    result = Replace(result, vbTab, "\t")
    EscapeJSON = result
End Function

Private Function ExtractContent(jsonResponse As String) As String
    ' Simple extraction - find "content":" and extract the value
    Dim startPos As Long, endPos As Long
    Dim content As String
    
    startPos = InStr(jsonResponse, """content"":""")
    If startPos = 0 Then
        ExtractContent = "Could not parse response"
        Exit Function
    End If
    
    startPos = startPos + 11 ' Length of "content":""
    
    ' Find the closing quote (accounting for escaped quotes)
    endPos = startPos
    Do
        endPos = InStr(endPos + 1, jsonResponse, """")
        If endPos = 0 Then Exit Do
        ' Check if it's escaped
        If Mid(jsonResponse, endPos - 1, 1) <> "\" Then Exit Do
    Loop
    
    If endPos > startPos Then
        content = Mid(jsonResponse, startPos, endPos - startPos)
        ' Unescape
        content = Replace(content, "\n", vbCrLf)
        content = Replace(content, "\""", """")
        content = Replace(content, "\\", "\")
        ExtractContent = content
    Else
        ExtractContent = "Could not parse response"
    End If
End Function

' ============================================
' OUTPUT
' ============================================

Private Sub ShowAndCopyFeedback(studentName As String, feedback As String)
    Dim result As VbMsgBoxResult
    
    ' Copy to clipboard
    CopyToClipboard feedback
    
    ' Show in a form or message box
    MsgBox "Feedback for " & studentName & " (copied to clipboard):" & vbCrLf & vbCrLf & _
           feedback, vbInformation, "DQ1 Feedback - Ready to Paste"
End Sub

Private Sub CopyToClipboard(text As String)
    Dim obj As Object
    Set obj = CreateObject("htmlfile")
    obj.parentWindow.clipboardData.SetData "text", text
    Set obj = Nothing
End Sub

' ============================================
' QUICK TEST - Run without API
' ============================================

Public Sub TestCheckerNoAPI()
    Dim ws As Worksheet
    Dim errors As Collection
    Dim errorText As String
    
    On Error GoTo ErrorHandler
    
    Set ws = ThisWorkbook.Worksheets("Basic Excel Formulas")
    Set errors = New Collection
    
    CheckInputCells ws, errors
    CheckBasicFormulas ws, errors
    CheckBasicFormatting ws, errors
    CheckRangeData ws, errors
    CheckRangeFormulas ws, errors
    CheckRangeFormatting ws, errors
    
    If errors.Count = 0 Then
        MsgBox "✓ No errors found!", vbInformation, "Test"
    Else
        errorText = BuildErrorText(errors)
        MsgBox "Found " & errors.Count & " issues:" & vbCrLf & vbCrLf & errorText, vbExclamation, "Test"
    End If
    
    Exit Sub
ErrorHandler:
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

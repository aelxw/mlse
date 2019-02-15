function doGet() {
  return HtmlService.createHtmlOutputFromFile('index');
}

function createForm(games, title, division){
  
  // Creates the Google Form
  
  var form = FormApp.create(title);
  form.setDescription("Select your preferred games.")
  
  form.addSectionHeaderItem().setTitle(division);
  
  var r1 = form.addMultipleChoiceItem()
  .setTitle("Which game is your 1st choice?")
  .setChoiceValues(games);
  
  var r2 = form.addMultipleChoiceItem()
  .setTitle("Which game is your 2nd choice?")
  .setChoiceValues(games);
  
  var r3 = form.addMultipleChoiceItem()
  .setTitle("Which game is your 3rd choice?")
  .setChoiceValues(games);
  
  r1.setRequired(true);
  
  form.setCollectEmail(true);
  
  return form.getEditUrl();
  
}


function getFormGames(formObj){
  
  // Extract the responses from the Google Form

  var games = [];
  var form = FormApp.openById(formObj["id"]);
  
  var matchUrl = "";
  
  try{
    matchUrl = SpreadsheetApp.openById(form.getDestinationId()).getUrl();
  }
  catch(err){
  }
  
  var division = form.getItems(FormApp.ItemType.SECTION_HEADER)[0].asSectionHeaderItem().getTitle();
  
  form.getItems(FormApp.ItemType.MULTIPLE_CHOICE)[0].asMultipleChoiceItem().getChoices().forEach(function(choice){
    games.push({"name":choice.getValue()});
  });
  
  var responses = {}
  
  var formResponses = form.getResponses();
  for (var i = 0; i < formResponses.length; i++) {
    var formResponse = formResponses[i];
    var itemResponses = formResponse.getItemResponses();
    var email = formResponse.getRespondentEmail();
    responses[email] = {}
    for (var j = 0; j < itemResponses.length; j++) {
      var itemResponse = itemResponses[j].getResponse();
      responses[email][j] = itemResponse;
    }
  }
  
  return {"games":games, "responses":responses, "division":division, "matchUrl":matchUrl};

}


function getActiveForms(){
  
  // Return all the active Google Forms
  
  var l = [];
  var fileIterator = DriveApp.getFilesByType("application/vnd.google-apps.form")
  while(fileIterator.hasNext()){
    var file = fileIterator.next();
    var form = FormApp.openById(file.getId())
    var responseLength = form.getResponses().length;
    var responseLengthString = "";
    if(responseLength != 1){
        responseLengthString = responseLength + " responses";
    }
    else{
        responseLengthString = responseLength + " response";
    }
    if(responseLength > 0){
      
      var isMatched = false;
      try{
        form.getDestinationId();
        isMatched = true;
      }
      catch(err){
        isMatched = false;
      }
      
      var temp = {
        "id": file.getId(),
        "name": file.getName(),
        "dateCreated": file.getDateCreated().getTime(),
        "responseLengthString": responseLengthString,
        "isMatched": isMatched
      }
      l.push(temp);
    }
  }
  return l;
}

function createSpreadsheet(selectedForm, matches){
  
  // Paste the matching solution into a Google Sheet
  // Highlights the matches
  
  var form = FormApp.openById(selectedForm.id);
  try{
      DriveApp.getFileById(form.getDestinationId()).setTrashed(true);
  }
  catch(err){   
  }
  
  var sheet = SpreadsheetApp.create(selectedForm.name + " Matches");
  sheet.getSheets()[0].setName("Matches");
  
  var rows = [];
  var ranks = [];
  
  var titleRow = ["Employee", "Rank 1", "Rank 2", "Rank 3"];
  rows.push(titleRow);
  
  for(var employee in matches){
    var choices = matches[employee]["choices"];
    var rank = parseInt(matches[employee]["rank"]);
    var row = [
      employee,
      choices[0],
      choices[1],
      choices[2]
    ]
    rows.push(row);
    ranks.push(rank);
  }
  
  var dataRange = sheet.getRange("A1:D" + rows.length);
  dataRange.setValues(rows);
  
  for(var i = 0; i < ranks.length; i++){
    if(ranks[i] > 0){
      var cell = dataRange.getCell(i+2, ranks[i]+1)
      cell.setBackground("yellow");
    }
  }
  
  for(var i = 1; i <= titleRow.length; i++){
    sheet.autoResizeColumn(i);
  }
  
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());
  
  return sheet.getUrl();
  
}

function loadMatchResults(selectedForm){
  
  // Looks at which cells are highlighted to get the matching results
  // Used to update historical matching data
  
  var form = FormApp.openById(selectedForm.id);
  var sheet = SpreadsheetApp.openById(form.getDestinationId()).getSheets()[1];
  
  var results = {};
  
  var rangeData = sheet.getDataRange();
  var lastColumn = rangeData.getLastColumn();
  var lastRow = rangeData.getLastRow();
  var searchRange = sheet.getRange("A2:D" + lastRow);
  
  for(var i = 1; i <= searchRange.getNumRows(); i++){
    var employee = searchRange.getCell(i, 1).getValue();
    results[employee] = 0;
    for(var j = searchRange.getNumColumns(); j > 1; j--){
      if(searchRange.getCell(i, j).getBackground() != "#ffffff"){
        results[employee] = j-1;
      }
    }
  }
  
  return results;
  
}




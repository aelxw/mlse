function doGet() {
  return HtmlService.createHtmlOutputFromFile('index');
}

var DIVISIONS = ["NBA", "NHL"];

function createForm(games, title, division){
  
  // Creates the Google Form
  
  var form = FormApp.create(title);
  
  var team = "";
  if (division == "NHL"){
    team = "Leafs";
  }
  if (division == "NBA"){
    team = "Raptors"
  }
  
  var description = "Your name has been drawn to receive two tickets to one of the following " + team + " games. Here is the list of games with their associated costs:\n\n";
  
  games.forEach(function(x){
    description += x+"\n"
  });
  
  description += "\nPlease list your preferred games below.\n\n"
  description += "By submitting this form, you acknowledge that you MUST ACCEPT tickets to any of your listed preferences and that you CANNOT decline the tickets once received."
  
  form.setDescription(description)
  
  form.addSectionHeaderItem().setTitle(division);
  
  form.addListItem()
  .setTitle("Which game is your 1st choice?")
  .setChoiceValues(games)
  .setRequired(true);
  
  form.addListItem()
  .setTitle("Which game is your 2nd choice? (Optional)")
  .setChoiceValues(games);
  
  form.addListItem()
  .setTitle("Which game is your 3rd choice? (Optional)")
  .setChoiceValues(games);
  
  form.addParagraphTextItem()
  .setTitle("Any additional comments? (Optional)");
  
  form.addCheckboxItem()
  .setTitle("I acknowledge that I MUST ACCEPT tickets to any of the games that I have submitted.")
  .setRequired(true);
  
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
  
  form.getItems(FormApp.ItemType.LIST)[0].asListItem().getChoices().forEach(function(choice){
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
      var itemResponse = itemResponses[j]
      if (itemResponse.getItem().getType() == FormApp.ItemType.LIST){
        responses[email][j] = itemResponse.getResponse(); 
      }
    }
  }
  
  return {"games":games, "responses":responses, "division":division, "matchUrl":matchUrl};
  
  
  
}


function getPastForms(){
  
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
    if(true){
      
      var isMatched = false;
      var sheetUrl = "";
      try{
        var id = form.getDestinationId();
        sheetUrl = DriveApp.getFileById(id).getUrl();
        isMatched = true;
      }
      catch(err){
        isMatched = false;
      }
      
      var division = ""
      try{
        division = form.getItems(FormApp.ItemType.SECTION_HEADER)[0].asSectionHeaderItem().getTitle();
      }
      catch(err){
        
      }
      
      var temp = {
        "id": file.getId(),
        "name": file.getName(),
        "dateCreated": file.getDateCreated().getTime(),
        "responseLengthString": responseLengthString,
        "isMatched": isMatched,
        "division": division,
        "url": file.getUrl(),
        "status": form.isAcceptingResponses() ? "OPEN" : "CLOSED",
        "sheetUrl": sheetUrl
      }
      
      if (DIVISIONS.indexOf(division) >= 0) {
        l.push(temp);
      }

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


function deleteFile(id){
  DriveApp.getFileById(id).setTrashed(true);
}

function deleteWave(pastForm){
  
  // Delete matching sheet if it exists
  if(pastForm.sheetUrl != ""){
    deleteFile(SpreadsheetApp.openByUrl(pastForm.sheetUrl).getId());
  }
  
  // Delete form
  deleteFile(pastForm.id);

}






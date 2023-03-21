// Define the variables to keep track of the state
let isHorizontal = true; // whether the highlight direction is horizontal or vertical
let startRow = 0; // the start row index of the highlighted cells
let startCol = 0; // the start column index of the highlighted cells
let highlightLength = 5; // the length of the highlighted cells

// function getSize() {
//   return size
// }

// highlightLength = getSize()

// Define the function to update the highlight based on the current state
var ships = [];
var filled = []
var numPlaced = 0
function updateHighlight() {
  const rows = document.querySelectorAll(".ocean tr");
  rows.forEach((row, rowIndex) => {
    const cells = row.querySelectorAll("td");
    cells.forEach((cell, colIndex) => {
      const isHighlighted =
        (isHorizontal &&
          rowIndex === startRow &&
          colIndex >= startCol &&
          colIndex < startCol + highlightLength) ||
        (!isHorizontal &&
          colIndex === startCol &&
          rowIndex >= startRow &&
          rowIndex < startRow + highlightLength);
      cell.classList.toggle("highlight", isHighlighted);
    });
  });
}

function setHighlight(event) {


  function included(square){

    var includedVar = false
    filled = filled.slice(0,runningTotal);
    filled.forEach(function (i){
     
      if (JSON.stringify(i)==JSON.stringify(square)){
        includedVar = true
        
  }})
  return includedVar
  }

  var overlap = false
  var placedSuccess = false
  const rows = document.querySelectorAll(".ocean tr");
  rows.forEach((row, rowIndex) => {
    const cells = row.querySelectorAll("td");
    cells.forEach((cell, colIndex) => {
      const isHighlighted =
        (isHorizontal &&
          rowIndex === startRow &&
          colIndex >= startCol &&
          colIndex < startCol + highlightLength) ||
        (!isHorizontal &&
          colIndex === startCol &&
          rowIndex >= startRow &&
          rowIndex < startRow + highlightLength);
      

          if (isHorizontal) {
            // col
            for (let i = 0; i < highlightLength; i++) {
              end = startCol + i;
              var square = [startRow,end];
              if (included(square)){
                overlap = true}
            }
          
          } else {
            //row
            for (let i = 0; i < highlightLength; i++) {
              end = startRow + i;
              var square = [end, startCol];
              if (included(square)){
                overlap = true;}
          }
        }
    });
  });

  rows.forEach((row, rowIndex) => {
    const cells = row.querySelectorAll("td");
    cells.forEach((cell, colIndex) => {
      const isHighlighted =
        (isHorizontal &&
          rowIndex === startRow &&
          colIndex >= startCol &&
          colIndex < startCol + highlightLength) ||
        (!isHorizontal &&
          colIndex === startCol &&
          rowIndex >= startRow &&
          rowIndex < startRow + highlightLength);
  
  if (isHighlighted  && !overlap) {
    cell.style.backgroundColor = "rgb(37, 36, 49)";
 


    if (isHorizontal) {
      // col
      for (let i = 0; i < highlightLength; i++) {
        end = startCol + i;
        var gridPlace = [startRow,end];
        if (!included(gridPlace)){
        filled.push(gridPlace)
        
        
        placedSuccess = true;


      }
      
    }
    } else {
      //row
      for (let i = 0; i < highlightLength; i++) {
        end = startRow + i;
        var gridPlace = [end, startCol];
        if (!included(gridPlace)){
          filled.push(gridPlace)
          
        

        placedSuccess = true;
        }
    }
  }
}
})})
if (placedSuccess){
  numPlaced+=1;
  var ship = [startRow, startCol, isHorizontal, highlightLength];
  ships.push(ship)
  console.log(ships)
}

}

// Define the function to handle the mouseover event

function sendUserInfo() {
  var row = startRow.toString();
  var col = startCol.toString();
  var horizontal = isHorizontal.toString();
  let userInfo = {
    'Carrier':ships[0],
    'Battleship':ships[1],
    'Destroyer':ships[2],
    'Submarine':ships[3],
    'Patrol Boat':ships[4],

    }
  const request = new XMLHttpRequest();
  request.open("POST", `/processUserInfo/${JSON.stringify(userInfo)}`);
  request.onload = () => {
    const flaskMessage = request.responseText;
    console.log(flaskMessage);
  };
  request.send();
  return userInfo;
}


const shipSize = [5, 4, 3, 3, 2];
const shipType = [
  "Carrier",
  "Battleship",
  "Destroyer",
  "Submarine",
  "Patrol Boat",
];
index = 0;
highlightLength = 5;
runningTotal = 0;
console.log(highlightLength);



function handleClick(event) {
  
  if (ships.length < 5) {

    const cell = event.target.closest("td");
    if (!cell) return;
    const row = cell.closest("tr");
    const rowIndex = Array.from(row.parentNode.children).indexOf(row);
    const colIndex = Array.from(row.children).indexOf(cell);
    if (isHorizontal) {
      startRow = rowIndex;
      startCol = colIndex;
    } else {
      startRow = rowIndex;
      startCol = colIndex;
    }
    if (isHorizontal) {
      end = startCol + highlightLength;
    } else {
      end = startRow + highlightLength;
    }
    if (end <= 11) {
      highlightLength = shipSize[numPlaced];
      runningTotal+=highlightLength
      updateHighlight();
      setHighlight();

      
      index +=1;
      highlightLength = shipSize[numPlaced];
      if (ships.length==5){
        sendUserInfo();
      }
    }
  }
}


// Define the function to handle the contextmenu event
function handleContextmenu(event) {
  event.preventDefault();
  isHorizontal = !isHorizontal;
  updateHighlight();
}

function handleMouseover(event) {
  highlightLength = shipSize[numPlaced];
  const cell = event.target.closest("td");
  if (!cell) return;
  const row = cell.closest("tr");
  const rowIndex = Array.from(row.parentNode.children).indexOf(row);
  const colIndex = Array.from(row.children).indexOf(cell);
  if (isHorizontal) {
    startRow = rowIndex;
    startCol = colIndex;
  } else {
    startRow = rowIndex;
    startCol = colIndex;
  }
  if (isHorizontal) {
    end = startCol + highlightLength;
  } else {
    end = startRow + highlightLength;
  }
  if (end <= 11) {
    updateHighlight();
  }
}

function getOceanDisplay(){
  $.ajax({
    url: '/displayOcean',
    type:'GET',
    success:function(board) {
      
      for (const key in board) {

        element = document.getElementById(key);
        if (board[key] != null){
          element.innerHTML = board[key];
        }
        
    }
  }
  });
}

function gameplay(){
  $.ajax({
    url: '/gameplay',
    type:'GET',
    success: function(){

    }
  })
}

function updateHighlightTarget() {
  highlightLength=1
  const rows = document.querySelectorAll(".target tr");
  rows.forEach((row, rowIndex) => {
    const cells = row.querySelectorAll("td");
    cells.forEach((cell, colIndex) => {
      const isHighlighted =
        (isHorizontal &&
          rowIndex === startRow &&
          colIndex >= startCol &&
          colIndex < startCol + highlightLength) ||
        (!isHorizontal &&
          colIndex === startCol &&
          rowIndex >= startRow &&
          rowIndex < startRow + highlightLength);
      cell.classList.toggle("highlight", isHighlighted);
    });
  });
}

function shootAt(event){
  highlightLength = 1
  const cell = event.target.closest("td");
    if (!cell) return;
    const row = cell.closest("tr");
    const rowIndex = Array.from(row.parentNode.children).indexOf(row);
    const colIndex = Array.from(row.children).indexOf(cell);
    if (isHorizontal) {
      startRow = rowIndex;
      startCol = colIndex;
    } else {
      startRow = rowIndex;
      startCol = colIndex;
    }
    if (isHorizontal) {
      end = startCol + highlightLength;
    } else {
      end = startRow + highlightLength;
    }
    if (end <= 11) {
      updateHighlightTarget();
    }
  }

  function shotAt(event){
      var row = startRow.toString();
      var col = startCol.toString();
      let userInfo = {
        'row':row.toString(),
        'col':col.toString(),
      }
      const request = new XMLHttpRequest();
      request.open("POST", `/processShot/${JSON.stringify(userInfo)}`);
      request.onload = () => {
        const flaskMessage = request.responseText;
        console.log(flaskMessage);
      };
      request.send();
      
      return userInfo;
  }

  function getTargetDisplay(){
    $.ajax({
      url: '/displayTarget',
      type:'GET',
      success:function(board) {
        console.log(board)
        
        for (const key in board) {
          let key2 = key.slice(0,-1);
          element = document.getElementById(key);
          if (board[key] == 'o'){
            element.innerHTML = 'O';
            element.style.backgroundColor = 'rgb(100,100,100)';
          }
          else if (board[key] != null){
            element.innerHTML = board[key];
            element.style.color = 'red';
            element.style.backgroundColor = 'rgb(120,100,100)';
          }
          
      }
    }
    });
   }

  function updateOcean(){
    $.ajax({
      url: '/updateOcean',
      type:'GET',
      success:function(board) {
        
        for (const key in board) {
          element = document.getElementById(key);
          if (board[key] == '\x1B[1m\x1B[38;5;196mx\x1B[0m'){
            element.style.color = 'red '
            element.style.backgroundColor = 'rgb(120,100,100)';
          }
          else if (board[key] == 'o'){
            element.innerHTML = 'O';
            element.style.backgroundColor = 'rgb(100,100,100)';
          }
          
      }
    }
    });
  }

  function updateTurn(){
    $.ajax({
      url: '/updateTurn',
      type:'GET'
    });
  }


// Attach the event listeners to the table
const table = document.querySelector(".ocean");

table.addEventListener("mouseover", handleMouseover);
table.addEventListener("contextmenu", handleContextmenu);
table.addEventListener("click", handleClick);


const target = document.querySelector(".target")
target.addEventListener("mouseover", shootAt);
target.addEventListener("click", shotAt);


console.log("Hello World");

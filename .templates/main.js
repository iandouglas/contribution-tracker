var labels = []
var authoredCommits = []
var coAuthoredCommits = []

for (const [name, commitCounts] of Object.entries(data)) {
  labels.push(name)
  authoredCommits.push(commitCounts["authored"]["total"])
  coAuthoredCommits.push(commitCounts["co-authored"]["total"])
}

var contributorCount = authoredCommits.length

var totalAuthoredCommits = 0
authoredCommits.forEach(element => totalAuthoredCommits += element)
var averageAuthoredCommits = totalAuthoredCommits / contributorCount

var totalCoAuthoredCommits = 0
coAuthoredCommits.forEach(element => totalCoAuthoredCommits += element)
var averageCoAuthoredCommits = totalCoAuthoredCommits / contributorCount

averageAuthoredData = []
averageCoAuthoredData = []

for(var i=0; i < contributorCount; i++){
  averageAuthoredData.push(averageAuthoredCommits)
  averageCoAuthoredData.push(averageCoAuthoredCommits)
}



var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: labels,
    datasets: [{
      label: 'Authored Commits',
      data: authoredCommits,
      backgroundColor: 'rgba(255, 99, 132, 0.2)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 1
    },
    {
      label: 'Co-Authored Commits',
      data: coAuthoredCommits,
      backgroundColor: "rgba(255, 159, 64, 0.2)",
      borderColor: "rgb(255, 159, 64, 1)",
      borderWidth: 1
    },
    {
      label: 'Average Authored Commits',
      data: averageAuthoredData,
      backgroundColor: 'rgba(0, 0, 0, 0.0)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 1,
      type: "line"
    },
    {
      label: 'Average Co-Authored Commits',
      data: averageCoAuthoredData,
      backgroundColor: "rgba(0, 0, 0, 0.0)",
      borderColor: "rgb(255, 159, 64, 1)",
      borderWidth: 1,
      type: "line"
    }]
  },
  options: {
    responsive: true,
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});


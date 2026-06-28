// show hide input searchbar
const searchBarContainer = document.getElementById('searchBarContainer');
const coverImageContainer = document.getElementById('coverImageContainer');
const showSearchBarButton = document.getElementById('showSearchBarButton');
const toggleIcon = document.getElementById('toggleIcon');

showSearchBarButton.addEventListener('click', () => {
    searchBarContainer.style.display = 'flex';
    coverImageContainer.style.display = 'none';
});

toggleIcon.addEventListener('click', () => {
    searchBarContainer.style.display = 'none';
    coverImageContainer.style.display = 'block';
});

 
// perform search on menu
let searchResult;
const menuContent = document.querySelector("ul.menu-inner");
const menuSearchedContent = document.querySelector("ul.menu-searched-inner");
const searchbar = document.querySelector(".search-input");
let searchTerm;

searchbar.addEventListener("input", (e)=>{
searchTerm = e.target.value;
menuSearchedContent.innerHTML = "";

if(searchTerm.length){
    menuContent.style.display = "none";

    const modules = menuContent.querySelectorAll("li.menu-item[data-is-module='true']");

    modules.forEach((singleModule) => {

        const moduleName = singleModule.querySelector("li.menu-item[data-is-module='true'] a div");
        const isSearched = moduleName.textContent.toLowerCase().includes(searchTerm.toLowerCase());

        // Clone the singleModule element to avoid modifying the original structure
        const clonedModule = singleModule.cloneNode(true);
        
        if (isSearched) {
            menuSearchedContent.appendChild(clonedModule);

             return;
          }
          
        const subModules = clonedModule.querySelectorAll("li.menu-item[data-is-sub-menu='true']");
        const subModulesToRemove = [];
        
        subModules.forEach((subModule) => {
        const subModuleName = subModule.querySelector("li.menu-item[data-is-sub-menu='true'] a div");
        const isSubSearched = subModuleName.textContent.toLowerCase().includes(searchTerm.toLowerCase());
        
        if (!isSubSearched) {
            subModulesToRemove.push(subModule);
        }
        });
        
        subModulesToRemove.forEach(subModule => {
            const parent = subModule.parentNode; 
            if (parent) { 
              parent.removeChild(subModule);
            }
          });
        

        const existingSubModules = clonedModule.querySelectorAll("li.menu-item[data-is-sub-menu='true']");

        
        if(existingSubModules.length) {
            // const searchedModuleName = clonedModule.querySelector("li.menu-item[data-is-module='true']");

            clonedModule.classList.add("open");

            console.log(clonedModule.classList);

            menuSearchedContent.appendChild(clonedModule);
        }

      });

} else{
    menuContent.style.display = "flex";
    menuSearchedContent.innerHTML="";
}

})






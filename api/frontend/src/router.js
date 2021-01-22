import SearchForm from './SearchForm.svelte';
import RegistrationForm from './RegistrationForm.svelte';
import Dataset from './Dataset.svelte';
import NotFound from './NotFound.svelte';
import Documentation from './Documentation.svelte';
import CreateDatasetForm from './CreateDatasetForm.svelte';

const initRouter = () => {
    const definedPaths = Object.freeze({
        "/": SearchForm,
        "/datasets/:dataset_id": Dataset,
        "/documentation": Documentation,
        "/registration": CreateDatasetForm
    });

    const definedPathArrays = Object.keys(definedPaths).map((path) => {return path.split("/")});

    function findMatch(pathArray) {
        function isSubPathMatch(subPathDefinition, subPath){
            let isMatch = false;

            if (subPathDefinition !== undefined && subPath !== undefined) {
                if (subPathDefinition.charAt(0) !== ':' && subPathDefinition === subPath) {
                    isMatch = true;
                } else if (subPathDefinition.charAt(0) === ':' && subPath !== undefined) {
                    isMatch = true;
                }
            }

            return isMatch
        }

        const isPathMatch = definedPathArrays.find((definedPathArray) => {
            return pathArray.every((subPath, idx) => {
                const definedSubPath = definedPathArray[idx];
                return isSubPathMatch(definedSubPath, subPath);
            });
        });

        if (isPathMatch !== undefined) {
            return isPathMatch.join("/");
        } else {
            return undefined;
        }
    }


    function renderPath(pathname) {
        const pathArray = pathname.split("/");

        const pathMatch = findMatch(pathArray);
       if (definedPaths[pathMatch] !== undefined) {
           return definedPaths[pathMatch]
       }  else {
           return NotFound
       }
    }

    return renderPath;
};

const Router = initRouter();
export default Router;
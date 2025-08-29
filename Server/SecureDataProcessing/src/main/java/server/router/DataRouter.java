package server.router;

import server.common.DataDto;

public class DataRouter {
    private void route(DataDto data){
        switch (data.getType()){
            case LOG:
                break;
            case FILE:
                break;
            case IMAGE:
                break;
            case JSON:
                break;
            case VIDEO:
                break;
            default:
                System.out.println("Unknown data type: " + data.getType());
        }
    }
}

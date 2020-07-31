def magic_recursive(bombs):
    count = bombs[0]//bombs[1]
    if bombs[0]%bombs[1]==0:
        if bombs[1]==1:
            return(count-1)
        else:
            return('impossible')
    bombs[0]=bombs[0]%bombs[1]
    bombs.reverse()
    gravy = magic_recursive(bombs)
    if gravy == 'impossible':
        return('impossible')
    return(count+gravy)
    

def bomb_baby(M, F):
    M,F=int(M),int(F)
    if M>=F:
        bombs=[M,F]
    else:
        bombs=[F,M]
        
    return(magic_recursive(bombs))

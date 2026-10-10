% Hechos
padre(juan, ana).
padre(juan, pedro).

% Regla
abuelo(X, Z) :-
    padre(X, Y),
    padre(Y, Z).

?- abuelo(juan, Quien).
